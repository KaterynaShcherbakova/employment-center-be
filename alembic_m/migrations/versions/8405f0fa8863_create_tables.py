"""Create tables

Revision ID: 8405f0fa8863
Revises: 
Create Date: 2022-11-18 02:09:48.174685

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8405f0fa8863'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('location',
    sa.Column('location_id', sa.Integer(), nullable=False),
    sa.Column('city', sa.String(length=80), nullable=False),
    sa.Column('country', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('location_id'),
    sa.UniqueConstraint('city', 'country')
    )
    op.create_table('person',
    sa.Column('person_id', sa.Integer(), nullable=False),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.Column('username', sa.String(length=45), nullable=False),
    sa.Column('password', sa.String(length=512), nullable=False),
    sa.Column('email', sa.String(length=45), nullable=False),
    sa.Column('firstName', sa.String(length=64), nullable=False),
    sa.Column('secondName', sa.String(length=64), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('role', sa.String(length=45), nullable=False),
    sa.ForeignKeyConstraint(['location_id'], ['location.location_id'], ),
    sa.PrimaryKeyConstraint('person_id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    op.create_table('experience',
    sa.Column('experience_id', sa.Integer(), nullable=False),
    sa.Column('beggining', sa.Date(), nullable=False),
    sa.Column('end', sa.Date(), nullable=True),
    sa.Column('job', sa.String(length=80), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['person_id'], ['person.person_id'], ),
    sa.PrimaryKeyConstraint('experience_id')
    )
    op.create_table('job',
    sa.Column('job_id', sa.Integer(), nullable=False),
    sa.Column('position', sa.String(length=80), nullable=False),
    sa.Column('salary', sa.Integer(), nullable=True),
    sa.Column('company', sa.String(length=80), nullable=False),
    sa.Column('online', sa.Boolean(), nullable=True),
    sa.Column('creator_id', sa.Integer(), nullable=True),
    sa.Column('location_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['creator_id'], ['person.person_id'], ),
    sa.ForeignKeyConstraint(['location_id'], ['location.location_id'], ),
    sa.PrimaryKeyConstraint('job_id')
    )
    op.create_table('application',
    sa.Column('application_id', sa.Integer(), nullable=False),
    sa.Column('person_id', sa.Integer(), nullable=True),
    sa.Column('job_id', sa.Integer(), nullable=True),
    sa.Column('dateOfApp', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['job_id'], ['job.job_id'], ),
    sa.ForeignKeyConstraint(['person_id'], ['person.person_id'], ),
    sa.PrimaryKeyConstraint('application_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('application')
    op.drop_table('job')
    op.drop_table('experience')
    op.drop_table('person')
    op.drop_table('location')
    # ### end Alembic commands ###
