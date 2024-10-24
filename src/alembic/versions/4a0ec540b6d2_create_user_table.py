"""Create organizations table

Revision ID: 4a0ec540b6d2
Revises:
Create Date: 2024-01-10 21:48:47.748804

"""

import uuid
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a0ec540b6d2"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.create_table(
        "organizations",
        sa.Column(
            "id",
            sa.UUID(as_uuid=True),
            primary_key=True,
            default=str(uuid.uuid4()),
            unique=True,
            nullable=False,
        ),
        sa.Column("organization_name", sa.String(100), unique=True, index=True, nullable=False),
        sa.Column(
            "organization_email",
            sa.String(100),
            unique=True,
            index=True,
            nullable=False,
        ),
        sa.Column("first_name", sa.String(100), nullable=True),
        sa.Column("last_name", sa.String(100), nullable=True),
        sa.Column("created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated", sa.DateTime(timezone=True), default=None, nullable=False),
        sa.Column("deleted", sa.DateTime(timezone=True), default=None, nullable=True),
    )


def downgrade():
    op.drop_table("organizations")
