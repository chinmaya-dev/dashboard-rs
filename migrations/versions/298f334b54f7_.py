"""empty message

Revision ID: 298f334b54f7
Revises: eb1e8f81d1b9
Create Date: 2019-03-23 10:57:26.625655

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '298f334b54f7'
down_revision = 'eb1e8f81d1b9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blog', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('platform', sa.Column('summary', sa.Text(), nullable=True))
    op.add_column('post', sa.Column('summary', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'summary')
    op.drop_column('platform', 'summary')
    op.drop_column('blog', 'summary')
    # ### end Alembic commands ###