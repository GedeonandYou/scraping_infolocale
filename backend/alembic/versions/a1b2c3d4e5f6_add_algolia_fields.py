"""Add Algolia-specific fields to scanned_events

Revision ID: a1b2c3d4e5f6
Revises: 605389200fa6
Create Date: 2026-03-20 00:00:00.000000

Nouveaux champs issus du hit Algolia (index memo_events) :
  - genre          : sous-catégorie (ex: "Animation")
  - annule         : événement annulé
  - complet        : événement complet/sold out
  - permanent      : événement permanent
  - accessibilites : tableau d'accessibilités (PMR, etc.)
  - ages           : tranches d'âge ciblées
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "605389200fa6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "scanned_events",
        sa.Column("genre", sa.String(255), nullable=True),
    )
    op.add_column(
        "scanned_events",
        sa.Column("annule", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "scanned_events",
        sa.Column("complet", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "scanned_events",
        sa.Column("permanent", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "scanned_events",
        sa.Column("accessibilites", postgresql.ARRAY(sa.Text()), nullable=True),
    )
    op.add_column(
        "scanned_events",
        sa.Column("ages", postgresql.ARRAY(sa.Text()), nullable=True),
    )

    # Index sur annule pour filtrer les événements non annulés
    op.create_index("ix_scanned_events_annule", "scanned_events", ["annule"])


def downgrade() -> None:
    op.drop_index("ix_scanned_events_annule", table_name="scanned_events")
    op.drop_column("scanned_events", "ages")
    op.drop_column("scanned_events", "accessibilites")
    op.drop_column("scanned_events", "permanent")
    op.drop_column("scanned_events", "complet")
    op.drop_column("scanned_events", "annule")
    op.drop_column("scanned_events", "genre")
