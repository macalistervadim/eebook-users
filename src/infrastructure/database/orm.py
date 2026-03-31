import uuid

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    MetaData,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import registry

from src.domain.model import EmailVerificationToken, OutboxEvent, User
from src.schemas.internal.auth import RefreshToken
from src.schemas.internal.role import UserRole

metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('first_name', String, nullable=False),
    Column('last_name', String, nullable=False),
    Column('email', String, nullable=False, unique=True, index=True),
    Column('username', String, nullable=False, unique=True, index=True),
    Column('hashed_password', String, nullable=False),
    Column('role', Enum(UserRole, name='userrole'), nullable=False, server_default='USER'),
    Column('is_verified', Boolean, nullable=False, server_default='false'),
    Column('is_disabled', Boolean, nullable=False, server_default='false'),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now()),
    Column('last_login_at', DateTime(timezone=True), nullable=True),
)

user_auth_state = Table(
    'user_auth_state',
    metadata,
    Column(
        'user_id',
        UUID(as_uuid=True),
        ForeignKey('users.id', ondelete='CASCADE'),
        primary_key=True,
    ),
    Column('failed_attempts', Integer, nullable=False, default=0),
    Column('token_version', Integer, nullable=False, default=0, server_default='0'),
    Column('locked_until', DateTime(timezone=True), nullable=True),
    Column('lock_count', Integer, nullable=False, default=0),
    Column('last_failed_at', DateTime(timezone=True), nullable=True),
    Column('updated_at', DateTime(timezone=True), server_default=func.now(), onupdate=func.now()),
)

refresh_tokens = Table(
    'refresh_tokens',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id'), nullable=False),
    Column('jti', String, nullable=False, index=True),
    Column('fingerprint', String, nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('expires_at', DateTime(timezone=True), nullable=False),
    Column('is_revoked', Boolean, default=False, nullable=False),
    Index('ix_refresh_tokens_user_id', 'user_id'),
    Index('ix_refresh_tokens_jti', 'jti', unique=True),
    Index('ix_refresh_tokens_expires_at', 'expires_at'),
)

email_verification_tokens = Table(
    'email_verification_tokens',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('user_id', UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
    Column('token_hash', String, nullable=False, unique=True),
    Column('expires_at', DateTime(timezone=True), nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('used_at', DateTime(timezone=True), nullable=True),
    Index('ix_email_verification_tokens_user_id', 'user_id'),
    Index('ix_email_verification_tokens_expires_at', 'expires_at'),
)

outbox_events = Table(
    'outbox_events',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('event_type', String, nullable=False),
    Column('routing_key', String, nullable=False),
    Column('payload', Text, nullable=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('published_at', DateTime(timezone=True), nullable=True),
    Column('attempts', Integer, nullable=False, server_default='0'),
    Column('error_message', Text, nullable=True),
    Index('ix_outbox_events_published_at', 'published_at'),
    Index('ix_outbox_events_created_at', 'created_at'),
)


def start_mappers():
    mapper_registry = registry()
    mapper_registry.map_imperatively(User, users)
    mapper_registry.map_imperatively(RefreshToken, refresh_tokens)
    mapper_registry.map_imperatively(EmailVerificationToken, email_verification_tokens)
    mapper_registry.map_imperatively(OutboxEvent, outbox_events)
