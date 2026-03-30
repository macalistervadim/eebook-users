"""Drop local user_subscription table after extraction to subscriptions service."""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'b4cf2b6f5d11'
down_revision: Union[str, Sequence[str], None] = 'ae0162dc8634'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('user_subscription')


def downgrade() -> None:
    raise NotImplementedError('user_subscription moved to eebook-subscriptions service')
