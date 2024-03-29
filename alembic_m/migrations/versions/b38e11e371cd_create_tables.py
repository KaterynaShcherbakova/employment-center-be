"""Create tables

Revision ID: b38e11e371cd
Revises: 3a9941a2fb3d
Create Date: 2022-11-24 20:31:19.657067

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b38e11e371cd'
down_revision = '3a9941a2fb3d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('application_job_id_fkey', 'application', type_='foreignkey')
    op.drop_constraint('application_person_id_fkey', 'application', type_='foreignkey')
    op.create_foreign_key(None, 'application', 'job', ['job_id'], ['job_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'application', 'person', ['person_id'], ['person_id'], ondelete='CASCADE')
    op.drop_constraint('job_creator_id_fkey', 'job', type_='foreignkey')
    op.create_foreign_key(None, 'job', 'person', ['creator_id'], ['person_id'], ondelete='CASCADE')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'job', type_='foreignkey')
    op.create_foreign_key('job_creator_id_fkey', 'job', 'person', ['creator_id'], ['person_id'])
    op.drop_constraint(None, 'application', type_='foreignkey')
    op.drop_constraint(None, 'application', type_='foreignkey')
    op.create_foreign_key('application_person_id_fkey', 'application', 'person', ['person_id'], ['person_id'])
    op.create_foreign_key('application_job_id_fkey', 'application', 'job', ['job_id'], ['job_id'])
    # ### end Alembic commands ###
