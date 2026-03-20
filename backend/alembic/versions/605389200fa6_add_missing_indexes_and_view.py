"""Add missing indexes and view

Revision ID: 605389200fa6
Revises: 9bc33c1d22ce
Create Date: 2026-02-04 11:31:43.909381

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '605389200fa6'
down_revision: Union[str, Sequence[str], None] = '9bc33c1d22ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing indexes and statistics view."""

    # Add index on users.email
    op.create_index('idx_users_email', 'users', ['email'], unique=False)

    # Add indexes on scanned_events
    op.create_index('idx_scanned_events_user', 'scanned_events', ['user_id'], unique=False)
    op.create_index('idx_scanned_events_coords', 'scanned_events', ['latitude', 'longitude'], unique=False)
    op.create_index('idx_scanned_events_begin_date', 'scanned_events', ['begin_date'], unique=False)
    op.create_index('idx_scanned_events_city', 'scanned_events', ['city'], unique=False)
    op.create_index('idx_scanned_events_category', 'scanned_events', ['category'], unique=False)

    # Add GIN index on raw_json for JSON queries
    op.execute('CREATE INDEX IF NOT EXISTS idx_scanned_events_raw_json ON scanned_events USING GIN(raw_json)')

    # Create statistics view
    op.execute("""
        CREATE OR REPLACE VIEW v_event_stats AS
        SELECT
            COUNT(*) as total_events,
            COUNT(DISTINCT city) as total_cities,
            COUNT(DISTINCT category) as total_categories,
            COUNT(CASE WHEN latitude IS NOT NULL THEN 1 END) as geocoded_events,
            COUNT(CASE WHEN is_private = TRUE THEN 1 END) as private_events,
            MIN(begin_date) as earliest_event,
            MAX(begin_date) as latest_event
        FROM scanned_events
    """)

    # Create cleanup function
    op.execute("""
        CREATE OR REPLACE FUNCTION cleanup_old_events(days_old INTEGER DEFAULT 365)
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            DELETE FROM scanned_events
            WHERE begin_date < NOW() - (days_old || ' days')::INTERVAL;

            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql
    """)

    # Add comments
    op.execute("COMMENT ON TABLE users IS 'Table des utilisateurs du système'")
    op.execute("COMMENT ON TABLE scanned_events IS 'Table des événements scrapés depuis Infolocale.fr'")
    op.execute("COMMENT ON COLUMN scanned_events.uid IS 'Identifiant unique pour déduplication'")
    op.execute("COMMENT ON COLUMN scanned_events.raw_json IS 'Données brutes JSON complètes de l''événement'")
    op.execute("COMMENT ON COLUMN scanned_events.latitude IS 'Latitude GPS obtenue via géocodage'")
    op.execute("COMMENT ON COLUMN scanned_events.longitude IS 'Longitude GPS obtenue via géocodage'")
    op.execute("COMMENT ON COLUMN scanned_events.place_id IS 'Identifiant du lieu (OpenRouteService ou Google Places)'")
    op.execute("COMMENT ON COLUMN scanned_events.rating IS 'Note du lieu (0.0 à 5.0)'")
    op.execute("COMMENT ON FUNCTION cleanup_old_events IS 'Supprimer les événements plus anciens que X jours (défaut: 365)'")


def downgrade() -> None:
    """Remove indexes, view and function."""

    # Drop function
    op.execute('DROP FUNCTION IF EXISTS cleanup_old_events(INTEGER)')

    # Drop view
    op.execute('DROP VIEW IF EXISTS v_event_stats')

    # Drop indexes
    op.execute('DROP INDEX IF EXISTS idx_scanned_events_raw_json')
    op.drop_index('idx_scanned_events_category', table_name='scanned_events')
    op.drop_index('idx_scanned_events_city', table_name='scanned_events')
    op.drop_index('idx_scanned_events_begin_date', table_name='scanned_events')
    op.drop_index('idx_scanned_events_coords', table_name='scanned_events')
    op.drop_index('idx_scanned_events_user', table_name='scanned_events')
    op.drop_index('idx_users_email', table_name='users')
