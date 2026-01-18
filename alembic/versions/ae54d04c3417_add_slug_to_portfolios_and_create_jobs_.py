"""Add slug to portfolios and create jobs table

Revision ID: ae54d04c3417
Revises: 
Create Date: 2026-01-10 05:31:35.005457

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy import Text
import uuid

# revision identifiers, used by Alembic.
revision = 'ae54d04c3417'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if slug column exists before adding
    connection = op.get_bind()
    inspector = sa.inspect(connection)
    portfolios_columns = [col['name'] for col in inspector.get_columns('portfolios')]
    
    # Add slug column to portfolios table (if it doesn't exist)
    if 'slug' not in portfolios_columns:
        op.add_column('portfolios', sa.Column('slug', sa.String(), nullable=True))
        op.create_index(op.f('ix_portfolios_slug'), 'portfolios', ['slug'], unique=True)
    
    # Check if jobs table exists
    tables = inspector.get_table_names()
    
    # Create jobs table (if it doesn't exist)
    if 'jobs' not in tables:
        op.create_table(
            'jobs',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('job_id', sa.String(), nullable=False),
            sa.Column('user_id', sa.String(), nullable=False),
            sa.Column('status', sa.String(), nullable=False),
            sa.Column('progress_percentage', sa.Integer(), nullable=False),
            sa.Column('current_stage', sa.String(), nullable=True),
            sa.Column('error_message', Text(), nullable=True),
            sa.Column('error_details', Text(), nullable=True),
            sa.Column('original_filename', sa.String(), nullable=True),
            sa.Column('file_size', sa.Integer(), nullable=True),
            sa.Column('file_type', sa.String(), nullable=True),
            sa.Column('started_at', sa.DateTime(), nullable=True),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('duration_seconds', sa.Float(), nullable=True),
            sa.Column('portfolio_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.ForeignKeyConstraint(['portfolio_id'], ['portfolios.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_jobs_job_id'), 'jobs', ['job_id'], unique=True)
        op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)
        op.create_index(op.f('ix_jobs_user_id'), 'jobs', ['user_id'], unique=False)
        op.create_index(op.f('ix_jobs_created_at'), 'jobs', ['created_at'], unique=False)
    else:
        # Table exists, check if indexes exist
        jobs_indexes = [idx['name'] for idx in inspector.get_indexes('jobs')]
        if 'ix_jobs_job_id' not in jobs_indexes:
            op.create_index(op.f('ix_jobs_job_id'), 'jobs', ['job_id'], unique=True)
        if 'ix_jobs_status' not in jobs_indexes:
            op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)
        if 'ix_jobs_user_id' not in jobs_indexes:
            op.create_index(op.f('ix_jobs_user_id'), 'jobs', ['user_id'], unique=False)
        if 'ix_jobs_created_at' not in jobs_indexes:
            op.create_index(op.f('ix_jobs_created_at'), 'jobs', ['created_at'], unique=False)
    
    # Create index on is_published for portfolios (if it doesn't exist)
    portfolio_indexes = [idx['name'] for idx in inspector.get_indexes('portfolios')]
    if 'ix_portfolios_is_published' not in portfolio_indexes:
        op.create_index(op.f('ix_portfolios_is_published'), 'portfolios', ['is_published'], unique=False)


def downgrade() -> None:
    # Drop jobs table
    op.drop_index(op.f('ix_jobs_created_at'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_user_id'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_job_id'), table_name='jobs')
    op.drop_table('jobs')
    
    # Remove slug column from portfolios
    try:
        op.drop_index(op.f('ix_portfolios_is_published'), table_name='portfolios')
    except:
        pass
    op.drop_index(op.f('ix_portfolios_slug'), table_name='portfolios')
    op.drop_column('portfolios', 'slug')


