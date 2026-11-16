"""reservation status and checks

Revision ID: 004
Revises: 003
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: str | Sequence[str] | None = "003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "reservations",
        sa.Column(
            "status", sa.String(length=20), server_default="pending", nullable=False
        ),
    )
    op.create_check_constraint(
        op.f("ck_reservations_status_valid"),
        "reservations",
        "status IN ('pending', 'confirmed', 'active', 'returned', 'cancelled')",
    )
    op.create_check_constraint(
        op.f("ck_reservations_dates_order"),
        "reservations",
        "end_date > start_date",
    )
    op.create_check_constraint(
        op.f("ck_reservations_total_price_non_negative"),
        "reservations",
        "total_price >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("ck_reservations_total_price_non_negative"), "reservations", type_="check"
    )
    op.drop_constraint(
        op.f("ck_reservations_dates_order"), "reservations", type_="check"
    )
    op.drop_constraint(
        op.f("ck_reservations_status_valid"), "reservations", type_="check"
    )
    op.drop_column("reservations", "status")
