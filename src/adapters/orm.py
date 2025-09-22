from sqlalchemy import Column, MetaData, String, Table
from sqlalchemy.orm import registry

from src.domain.model import User

metadata = MetaData()

users = Table(
    name="users",
    metadata=metadata,
    columns=[
        Column("id", String, primary_key=True),
        Column("first_name", String),
        Column("last_name", String),
        Column("email", String),
    ],
)


def start_mappers():
    mapper_registry = registry()
    mapper_registry.map_imperatively(User, users)
