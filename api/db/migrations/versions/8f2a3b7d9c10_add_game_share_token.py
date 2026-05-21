"""Add game share token

Revision ID: 8f2a3b7d9c10
Revises: 55af41880868
Create Date: 2026-05-20 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8f2a3b7d9c10"
down_revision: Union[str, None] = "55af41880868"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("games", sa.Column("share_token", sa.String(length=64), nullable=True))
    op.create_index(op.f("ix_games_share_token"), "games", ["share_token"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_games_share_token"), table_name="games")
    op.drop_column("games", "share_token")
