import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

import aio_pika
from aio_pika import DeliveryMode, Message, RobustChannel, RobustConnection

from src.infrastructure.database.engine import get_session_factory
from src.infrastructure.database.repository.factory import SqlAlchemyOutboxEventRepositoryFactory

logger = logging.getLogger(__name__)


class RabbitPublisher:
    def __init__(self, connection: RobustConnection, exchange_name: str) -> None:
        self._connection = connection
        self._exchange_name = exchange_name
        self._channel: RobustChannel | None = None

    async def _channel_or_create(self) -> RobustChannel:
        if self._channel is None or self._channel.is_closed:
            self._channel = await self._connection.channel()
            await self._channel.set_qos(prefetch_count=10)
        return self._channel

    async def publish(self, *, routing_key: str, payload: str, message_id: str) -> None:
        channel = await self._channel_or_create()
        exchange = await channel.declare_exchange(
            self._exchange_name,
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )
        await exchange.publish(
            Message(
                body=payload.encode(),
                content_type='application/json',
                delivery_mode=DeliveryMode.PERSISTENT,
                message_id=message_id,
                timestamp=datetime.now(UTC),
            ),
            routing_key=routing_key,
        )


class RabbitOutboxRelay:
    def __init__(
        self,
        *,
        publisher: RabbitPublisher,
        poll_interval_seconds: float = 2.0,
        batch_size: int = 50,
    ) -> None:
        self._publisher = publisher
        self._poll_interval_seconds = poll_interval_seconds
        self._batch_size = batch_size
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        if self._task is not None:
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._run(), name='users-rabbit-outbox-relay')

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None

    async def _run(self) -> None:
        session_factory = get_session_factory()
        repo_factory = SqlAlchemyOutboxEventRepositoryFactory()

        while not self._stop_event.is_set():
            try:
                async with session_factory() as session:
                    repo = repo_factory.create(session)
                    events = await repo.list_pending(limit=self._batch_size)
                    if not events:
                        await session.rollback()
                        await asyncio.wait_for(
                            self._stop_event.wait(),
                            timeout=self._poll_interval_seconds,
                        )
                        continue

                    for event in events:
                        try:
                            await self._publisher.publish(
                                routing_key=event.routing_key,
                                payload=event.payload,
                                message_id=str(event.id),
                            )
                            event.mark_published(datetime.now(UTC))
                        except Exception as exc:  # noqa: BLE001
                            logger.exception('Failed to publish outbox event id=%s', event.id)
                            event.mark_failed(str(exc))
                        await repo.save(event)
                    await session.commit()
            except TimeoutError:
                continue
            except Exception:  # noqa: BLE001
                logger.exception('Outbox relay iteration failed')
                await asyncio.sleep(self._poll_interval_seconds)


class RabbitOutboxRelaySupervisor:
    def __init__(
        self,
        *,
        url: str,
        exchange_name: str,
        retry_delay_seconds: float = 5.0,
    ) -> None:
        self._url = url
        self._exchange_name = exchange_name
        self._retry_delay_seconds = retry_delay_seconds
        self._task: asyncio.Task | None = None
        self._stop_event = asyncio.Event()

    async def start(self) -> None:
        if self._task is not None:
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(
            self._run(),
            name='users-rabbit-outbox-relay-supervisor',
        )

    async def stop(self) -> None:
        if self._task is None:
            return
        self._stop_event.set()
        await self._task
        self._task = None

    async def _run(self) -> None:
        while not self._stop_event.is_set():
            relay: RabbitOutboxRelay | None = None
            try:
                logger.info('Starting RabbitMQ outbox relay')
                async with rabbit_connection(self._url) as connection:
                    relay = RabbitOutboxRelay(
                        publisher=RabbitPublisher(connection, self._exchange_name),
                    )
                    await relay.start()
                    logger.info('RabbitMQ outbox relay started')
                    await self._stop_event.wait()
            except Exception:  # noqa: BLE001
                if self._stop_event.is_set():
                    break
                logger.exception('RabbitMQ outbox relay crashed or failed to connect')
                try:
                    await asyncio.wait_for(
                        self._stop_event.wait(),
                        timeout=self._retry_delay_seconds,
                    )
                except TimeoutError:
                    continue
            finally:
                if relay is not None:
                    await relay.stop()


@asynccontextmanager
async def rabbit_connection(url: str) -> AsyncIterator[RobustConnection]:
    connection = await aio_pika.connect_robust(url)
    try:
        yield connection
    finally:
        await connection.close()
