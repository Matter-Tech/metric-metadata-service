"""Making non required filleds to allow null values

Revision ID: 503dd94329fa
Revises: 918d1687226c
Create Date: 2024-11-09 15:52:47.778147

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "503dd94329fa"
down_revision: Union[str, None] = "918d1687226c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###