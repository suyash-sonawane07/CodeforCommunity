"""Database integration tests — auto-skip when PostgreSQL/PostGIS is not running.

Run the full stack (or `make db-up db-migrate db-seed`) to enable these.
"""

import pytest
from sqlalchemy import text

from app.db.session import engine


def _db_available() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001
        return False


pytestmark = pytest.mark.skipif(not _db_available(), reason="PostgreSQL not reachable")


def test_postgis_extension_available():
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT EXISTS(SELECT 1 FROM pg_extension WHERE extname='postgis')")
        ).scalar()
    assert row is True, "PostGIS extension missing — run migrations (make db-migrate)"


def test_all_prd_tables_exist():
    expected = {
        "users", "citizen_requests", "request_transcriptions", "extracted_entities",
        "locations", "needs_clusters", "cluster_members", "infrastructure_assets",
        "demographic_indicators", "public_datasets", "projects", "gap_analyses",
        "priority_factors", "evidence_records", "simulation_scenarios",
        "review_actions", "interventions", "audit_logs",
    }
    with engine.connect() as conn:
        present = {
            r[0]
            for r in conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            )
        }
    missing = expected - present
    assert not missing, f"tables missing (run migrations): {missing}"


def test_locations_geometry_column_is_postgis():
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT type, srid FROM geometry_columns "
                "WHERE f_table_name='locations' AND f_geometry_column='geom'"
            )
        ).first()
    assert row is not None, "locations.geom is not a PostGIS geometry column"
    assert row[0].upper() == "POINT" and row[1] == 4326


def test_seed_data_present():
    from app.models import PublicDataset

    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        seed = db.query(PublicDataset).filter(PublicDataset.source_label == "synthetic").first()
        assert seed is not None, "seed missing — run `make db-seed`"
        assert seed.version.startswith("synthetic_")
    finally:
        db.close()
