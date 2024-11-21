"""Initial Migration

Revision ID: c6891eb27329
Revises: 
Create Date: 2024-11-21 18:32:49.187044

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c6891eb27329'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('data_metrics',
    sa.Column('data_id', sa.UUID(), nullable=False, comment='Field used to store the UUID to the data nodes which are updated every quarter.'),
    sa.Column('metric_type', sa.String(length=50), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('deleted', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_metrics_data_id'), 'data_metrics', ['data_id'], unique=False)
    op.create_index(op.f('ix_data_metrics_metric_type'), 'data_metrics', ['metric_type'], unique=False)
    op.create_index(op.f('ix_data_metrics_name'), 'data_metrics', ['name'], unique=False)
    op.create_table('events',
    sa.Column('event_type', sa.Enum('CREATED', 'UPDATED', 'DELETED', name='eventtypeenum'), nullable=False),
    sa.Column('entity_type', sa.Enum('METRIC_SET', 'METRIC_SET_TREE', 'METRIC', 'DATA_METRIC', 'PROPERTY', name='entitytypeenum'), nullable=False),
    sa.Column('node_id', sa.UUID(), nullable=False),
    sa.Column('user_id', sa.UUID(), nullable=True),
    sa.Column('new_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('deleted', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_events_entity_type'), 'events', ['entity_type'], unique=False)
    op.create_index(op.f('ix_events_node_id'), 'events', ['node_id'], unique=False)
    op.create_table('metric_sets',
    sa.Column('status', sa.Enum('DEPLOYED', 'NOT_USED', name='statusenum'), nullable=False),
    sa.Column('short_name', sa.String(length=100), nullable=False),
    sa.Column('placement', sa.Enum('ESG_INSIGHTS', 'SDGS', 'REGULATORY', 'COLLECTIONS', name='placementenum'), nullable=False),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('deleted', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('properties',
    sa.Column('property_name', sa.String(length=100), nullable=False),
    sa.Column('property_description', sa.Text(), nullable=True),
    sa.Column('data_type', sa.Enum('STRING', 'NUMBER', 'UUID', 'BOOLEAN', name='datatypeenum'), nullable=False),
    sa.Column('entity_type', sa.Enum('METRIC_SET', 'METRIC_SET_TREE', 'METRIC', 'DATA_METRIC', 'PROPERTY', name='entitytypeenum'), nullable=False),
    sa.Column('is_required', sa.Boolean(), nullable=False),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('deleted', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_properties_entity_type'), 'properties', ['entity_type'], unique=False)
    op.create_index(op.f('ix_properties_property_name'), 'properties', ['property_name'], unique=False)
    op.create_table('metric_set_trees',
    sa.Column('metric_set_id', sa.UUID(), nullable=False),
    sa.Column('node_type', sa.Enum('ROOT', 'CATEGORY', 'METRIC', 'SECTION', 'CHART', name='nodetypeenum'), nullable=False),
    sa.Column('node_depth', sa.Integer(), nullable=False),
    sa.Column('node_name', sa.String(length=100), nullable=True),
    sa.Column('node_description', sa.Text(), nullable=True),
    sa.Column('node_reference_id', sa.String(length=100), nullable=True),
    sa.Column('node_special', sa.String(length=100), nullable=True),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('deleted', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['metric_set_id'], ['metric_sets.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('metrics',
    sa.Column('metric_set_id', sa.UUID(), nullable=False),
    sa.Column('parent_section_id', sa.UUID(), nullable=True),
    sa.Column('parent_metric_id', sa.UUID(), nullable=True),
    sa.Column('data_metric_id', sa.UUID(), nullable=True),
    sa.Column('status', sa.Enum('DEPLOYED', 'NOT_USED', name='statusenum'), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('name_suffix', sa.String(length=50), nullable=True),
    sa.Column('meta_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('deleted', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created', sa.DateTime(timezone=True), nullable=False),
    sa.Column('updated', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['data_metric_id'], ['data_metrics.id'], ),
    sa.ForeignKeyConstraint(['metric_set_id'], ['metric_sets.id'], ),
    sa.ForeignKeyConstraint(['parent_metric_id'], ['metrics.id'], ),
    sa.ForeignKeyConstraint(['parent_section_id'], ['metric_set_trees.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metric_metric_set_id_status', 'metrics', ['metric_set_id', 'status'], unique=False)
    op.create_index(op.f('ix_metrics_data_metric_id'), 'metrics', ['data_metric_id'], unique=False)
    op.create_index(op.f('ix_metrics_metric_set_id'), 'metrics', ['metric_set_id'], unique=False)
    op.create_index(op.f('ix_metrics_parent_metric_id'), 'metrics', ['parent_metric_id'], unique=False)
    op.create_index(op.f('ix_metrics_parent_section_id'), 'metrics', ['parent_section_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_metrics_parent_section_id'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_parent_metric_id'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_metric_set_id'), table_name='metrics')
    op.drop_index(op.f('ix_metrics_data_metric_id'), table_name='metrics')
    op.drop_index('ix_metric_metric_set_id_status', table_name='metrics')
    op.drop_table('metrics')
    op.drop_table('metric_set_trees')
    op.drop_index(op.f('ix_properties_property_name'), table_name='properties')
    op.drop_index(op.f('ix_properties_entity_type'), table_name='properties')
    op.drop_table('properties')
    op.drop_table('metric_sets')
    op.drop_index(op.f('ix_events_node_id'), table_name='events')
    op.drop_index(op.f('ix_events_entity_type'), table_name='events')
    op.drop_table('events')
    op.drop_index(op.f('ix_data_metrics_name'), table_name='data_metrics')
    op.drop_index(op.f('ix_data_metrics_metric_type'), table_name='data_metrics')
    op.drop_index(op.f('ix_data_metrics_data_id'), table_name='data_metrics')
    op.drop_table('data_metrics')
    # ### end Alembic commands ###
