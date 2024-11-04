"""create orders table

Revision ID: 0001
Revises: 
Create Date: 2024-11-04 16:36:19.053781

"""
import uuid

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "orders",
        sa.Column("id", UUID, primary_key=True, default=lambda: str(uuid.uuid4())),
        sa.Column("customer_name", sa.String(255), nullable=False),
        sa.Column("total_amount", sa.Float, nullable=False),
        sa.Column("currency", sa.String(16), nullable=False),
        sa.Column(
            "status",
            sa.Enum("Pending", "Shipped", "Delivered", name="orderstatus"),
            nullable=False,
            default="Pending",
        ),
    )


def downgrade():
    op.drop_table("orders")
    op.execute("DROP TYPE orderstatus")
