"""empty message

Revision ID: 4c364f848c3
Revises: 19e28e1e2ce8
Create Date: 2015-01-08 14:47:25.966795

"""

# revision identifiers, used by Alembic.
revision = '4c364f848c3'
down_revision = '19e28e1e2ce8'

from alembic import op
import sqlalchemy as sa

connection = op.get_bind()

plot_helper = sa.Table('plot', sa.MetaData(),
                       sa.Column('id', sa.Integer, primary_key=True),
                       sa.Column('crawl_id', sa.Integer(), nullable=True),
                       sa.ForeignKeyConstraint(['crawl_id'], ['crawl.id'], ),
                      )

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('plot', sa.Column('crawl_id', sa.String(length=64), nullable=True))
    for plot in connection.execute(plot_helper.select()):
        connection.execute(
            plot_helper.update().where(
                plot_helper.c.id == plot.id
            )
        )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('plot', 'crawl_id')
    ### end Alembic commands ###
