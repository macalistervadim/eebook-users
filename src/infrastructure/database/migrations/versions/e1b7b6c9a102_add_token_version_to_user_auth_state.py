"""Add durable token version to user_auth_state."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = 'e1b7b6c9a102'
down_revision: Union[str, Sequence[str], None] = 'b4cf2b6f5d11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'user_auth_state',
        sa.Column('token_version', sa.Integer(), nullable=False, server_default=text('0')),
    )


def downgrade() -> None:
    op.drop_column('user_auth_state', 'token_version')
