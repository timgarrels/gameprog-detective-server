"""empty message

Revision ID: 69a8b8a99c67
Revises: 
Create Date: 2019-12-30 19:03:50.479795

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69a8b8a99c67'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('task',
    sa.Column('task_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('description', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('task_id')
    )
    op.create_table('user',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('telegram_handle', sa.String(length=64), nullable=True),
    sa.Column('telegram_start_token', sa.String(length=64), nullable=False),
    sa.Column('requested_data_types', sa.String(length=64), nullable=True),
    sa.Column('current_story_point', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('telegram_handle')
    )
    op.create_table('contact',
    sa.Column('contact_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('firstname', sa.String(length=64), nullable=True),
    sa.Column('lastname', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('contact_id')
    )
    op.create_table('task_assignment',
    sa.Column('task_assignment_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('task_id', sa.Integer(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['task_id'], ['task.task_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], ),
    sa.PrimaryKeyConstraint('task_assignment_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task_assignment')
    op.drop_table('contact')
    op.drop_table('user')
    op.drop_table('task')
    # ### end Alembic commands ###