"""Create property unique constraint

Revision ID: 2d10f69d0da4
Revises: c6891eb27329
Create Date: 2025-01-04 13:00:24.197436

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d10f69d0da4'
down_revision: Union[str, None] = 'c6891eb27329'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('uq_property_name_entity_type', 'properties', ['property_name', 'entity_type'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('uq_property_name_entity_type', 'properties', type_='unique')
    # ### end Alembic commands ###
