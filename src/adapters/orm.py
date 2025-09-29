import uuid

from sqlalchemy import UUID, Column, MetaData, String, Table
from sqlalchemy.orm import registry

from src.domain.model import User

metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('first_name', String),
    Column('last_name', String),
    Column('email', String),
)


def start_mappers():
    mapper_registry = registry()
    mapper_registry.map_imperatively(User, users)
