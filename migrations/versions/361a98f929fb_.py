"""empty message

Revision ID: 361a98f929fb
Revises: 0294d6131dc3
Create Date: 2021-05-09 13:01:50.371838

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '361a98f929fb'
down_revision = '0294d6131dc3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team', schema=None) as batch_op:
        batch_op.drop_column('created_at')

    # ### end Alembic commands ###
