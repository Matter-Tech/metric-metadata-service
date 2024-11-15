"""Removed timestamp as property of event

Revision ID: 65f5c048833b
Revises: 38737c2e1f07
Create Date: 2024-11-14 17:59:03.238130

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "65f5c048833b"
down_revision: Union[str, None] = "38737c2e1f07"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("events", "timestamp")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "events", sa.Column("timestamp", postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=False)
    )
    # ### end Alembic commands ###