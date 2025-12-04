import uuid

from sqlalchemy import (
    UUID,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    MetaData,
    String,
    Table,
    func,
)
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


def start_mappers():
    mapper_registry = registry()
    mapper_registry.map_imperatively(User, users)
