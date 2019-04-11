"""empty message

Revision ID: eb1e8f81d1b9
Revises: 4a9d49e42ebc
Create Date: 2019-03-23 10:00:51.534437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'eb1e8f81d1b9'
down_revision = '4a9d49e42ebc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('blog', sa.Column('image_file', sa.String(length=20), nullable=True))
    op.add_column('platform', sa.Column('image_file', sa.String(length=20), nullable=True))
    op.add_column('post', sa.Column('image_file', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('post', 'image_file')
    op.drop_column('platform', 'image_file')
    op.drop_column('blog', 'image_file')
    # ### end Alembic commands ###