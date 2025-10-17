import uuid

from sqlalchemy import UUID, Boolean, Column, DateTime, MetaData, String, Table, func
from sqlalchemy.orm import registry

from src.domain.model import User

metadata = MetaData()

users = Table(
    'users',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
    Column('first_name', String, nullable=False),
    Column('last_name', String, nullable=False),
    Column('email', String, nullable=False),
    Column('username', String, nullable=True),
    Column('hashed_password', String, nullable=False),
    Column('is_active', Boolean, default=True),
    Column('is_verified', Boolean, default=False),
    Column('created_at', DateTime(timezone=True), server_default=func.now()),
    Column('updated_at', DateTime(timezone=True), server_default=func.now()),
    Column('last_login_at', DateTime(timezone=True), nullable=True),
)


def start_mappers():
    mapper_registry = registry()
    mapper_registry.map_imperatively(User, users)
