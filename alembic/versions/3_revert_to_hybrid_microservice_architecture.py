"""revert to hybrid microservice architecture

Revision ID: 3
Revises: 2
Create Date: 2025-09-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3'
down_revision: Union[str, None] = '2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the current users table
    op.drop_index('ix_users_username', table_name='users')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')
    
    # Create the auth_users table for referential integrity
    op.create_table('auth_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_auth_users_id', 'id'),
    )
    
    # Create the users table with the hybrid schema
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.Index('ix_users_id', 'id'),
        sa.Index('ix_users_username', 'username'),
    )
    
    # Add foreign key constraints to badges and learning_goals
    op.add_column('badges', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_badges_user_id', 'badges', 'auth_users', ['user_id'], ['id'])
    op.drop_constraint('fk_badges_user_id', 'badges', type_='foreignkey')
    
    op.add_column('learning_goals', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_learning_goals_user_id', 'learning_goals', 'auth_users', ['user_id'], ['id'])
    op.drop_constraint('fk_learning_goals_user_id', 'learning_goals', type_='foreignkey')


def downgrade() -> None:
    # Drop the tables
    op.drop_constraint('fk_badges_user_id', 'badges', type_='foreignkey')
    op.drop_column('badges', 'user_id')
    op.drop_constraint('fk_learning_goals_user_id', 'learning_goals', type_='foreignkey')
    op.drop_column('learning_goals', 'user_id')
    
    op.drop_table('users')
    op.drop_table('auth_users')
    
    # Recreate the previous schema
    op.create_table('users',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('username', sa.String(50), nullable=False),
        sa.Column('email', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('display_name', sa.String(100), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('avatar_url', sa.Text(), nullable=True),
        sa.Column('location', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    # Create indexes
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_username', 'users', ['username'])