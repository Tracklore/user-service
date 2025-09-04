"""migrate to microservice architecture

Revision ID: 1
Revises: 
Create Date: 2025-08-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create the users table (this replaces the old users table and auth_users table)
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('bio', sa.String(), nullable=True),
        sa.Column('skills', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('username'),
        sa.Index('ix_users_id', 'id'),
        sa.Index('ix_users_username', 'username'),
    )
    
    # Add foreign key constraints to badges and learning_goals
    op.add_column('badges', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_badges_user_id', 'badges', 'users', ['user_id'], ['id'])
    op.drop_constraint('badges_owner_id_fkey', 'badges', type_='foreignkey')
    op.drop_column('badges', 'owner_id')
    op.drop_column('badges', 'auth_user_id')
    
    op.add_column('learning_goals', sa.Column('user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_learning_goals_user_id', 'learning_goals', 'users', ['user_id'], ['id'])
    op.drop_constraint('learning_goals_owner_id_fkey', 'learning_goals', type_='foreignkey')
    op.drop_column('learning_goals', 'owner_id')
    op.drop_column('learning_goals', 'auth_user_id')


def downgrade() -> None:
    # Recreate the old structure
    op.drop_constraint('fk_badges_user_id', 'badges', type_='foreignkey')
    op.drop_column('badges', 'user_id')
    op.drop_constraint('fk_learning_goals_user_id', 'learning_goals', type_='foreignkey')
    op.drop_column('learning_goals', 'user_id')
    
    # Drop the users table
    op.drop_table('users')
    
    # Recreate the auth_users table
    op.create_table('auth_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_auth_users_id', 'id'),
    )
    
    # Restore the old foreign key constraints
    op.add_column('badges', sa.Column('auth_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_badges_auth_user_id', 'badges', 'auth_users', ['auth_user_id'], ['id'])
    op.add_column('learning_goals', sa.Column('auth_user_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_learning_goals_auth_user_id', 'learning_goals', 'auth_users', ['auth_user_id'], ['id'])