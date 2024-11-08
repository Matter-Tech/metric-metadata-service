"""Create property table

Revision ID: 372d9d9803c4
Revises: 4a0ec540b6d2
Create Date: 2024-10-31 21:38:03.139194

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "372d9d9803c4"
down_revision: Union[str, None] = "4a0ec540b6d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "properties",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("property_name", sa.String(length=100), nullable=False),
        sa.Column("property_description", sa.Text(), nullable=True),
        sa.Column("data_type", sa.Enum("STRING", "NUMBER", "BOOLEAN", "DATETIME", name="datatypeenum"), nullable=False),
        sa.Column(
            "entity_type",
            sa.Enum("METRIC", "METRIC_SET", "METRIC_HIERARCHY", "METRIC_DATA", name="entitytypeenum"),
            nullable=False,
        ),
        sa.Column("is_required", sa.Boolean(), nullable=False),
        sa.Column("deleted", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_properties_entity_type"), "properties", ["entity_type"], unique=False)
    op.create_index(op.f("ix_properties_property_description"), "properties", ["property_description"], unique=True)
    op.create_index(op.f("ix_properties_property_name"), "properties", ["property_name"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_properties_property_name"), table_name="properties")
    op.drop_index(op.f("ix_properties_property_description"), table_name="properties")
    op.drop_index(op.f("ix_properties_entity_type"), table_name="properties")
    op.drop_table("properties")
    # ### end Alembic commands ###
