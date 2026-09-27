"""Minimal SYNTHETIC seed data — structurally valid rows only (brief §9).

Run: `make db-seed` → `python -m app.db.seed`.

These rows exist to verify DB connectivity, API serialisation and the
cluster/location/infrastructure/project relations. They are NOT fake production
statistics. Everything here is SYNTHETIC (FR-057) — see data/synthetic/README.md.
"""

from __future__ import annotations

import sys

from geoalchemy2 import WKTElement

from app.db.session import SessionLocal
from app.models import (
    DemographicIndicator,
    InfrastructureAsset,
    Location,
    NeedsCluster,
    Project,
    PublicDataset,
    User,
)

SYNTHETIC_LABEL = "SYNTHETIC — not real data (FR-057)"


def seed() -> None:
    db = SessionLocal()
    try:
        if db.query(PublicDataset).first():
            print("Seed already applied — skipping (use make db-reset to reseed)")
            return

        # --- dataset registry -------------------------------------------------
        demo = PublicDataset(
            name="civicpulse_demo_seed",
            source_label="synthetic",  # FR-038 provenance
            version="synthetic_v0.1",
            description=SYNTHETIC_LABEL,
        )
        db.add(demo)
        db.flush()

        # --- users (demo logins, PRD §5) --------------------------------------
        for name, email, role in [
            ("Demo Analyst", "analyst@civicpulse.dev", "analyst"),
            ("Demo Reviewer", "reviewer@civicpulse.dev", "reviewer"),
            ("Demo Decision-Maker", "decision@civicpulse.dev", "decision_maker"),
            ("Demo Admin", "admin@civicpulse.dev", "admin"),
        ]:
            db.add(User(name=name, email=email, role=role))

        # --- locations (2, PostGIS geometry, mid confidence) -------------------
        village = Location(
            state="Demo State",
            district="Demo District 1",
            block="Demo Block A",
            village_ward="Demo Village 1",
            latitude=19.876,
            longitude=75.343,
            geom=WKTElement("POINT(75.343 19.876)", srid=4326),
            confidence=0.82,
            resolution_method="gazetteer_exact",
            source_text="Demo Village 1, Demo Block A",
        )
        town = Location(
            state="Demo State",
            district="Demo District 2",
            block="Demo Block B",
            village_ward="Demo Town 2",
            latitude=19.990,
            longitude=75.180,
            geom=WKTElement("POINT(75.180 19.990)", srid=4326),
            confidence=0.64,
            resolution_method="gazetteer_fuzzy",
            source_text="near the bus stand, Demo Town 2",
        )
        db.add_all([village, town])
        db.flush()

        # --- cluster (forming, 2 members conceptually) --------------------------
        cluster = NeedsCluster(
            issue_type="transport_access",
            status="forming",
            independent_demand_count=2,
            raw_message_count=3,
            location_id=village.id,
            uncertainty_notes=["Seed example — SYNTHETIC inputs only"],
            dataset_version=demo.version,
        )
        db.add(cluster)

        # --- infrastructure + demographics + project ---------------------------
        db.add(
            InfrastructureAsset(
                asset_type="bus_stop",
                name="Demo Bus Stop (synthetic)",
                location_id=town.id,
                dataset_version=demo.version,
            )
        )
        db.add(
            DemographicIndicator(
                location_id=village.id,
                population=2100,
                deprivation_index=0.55,
                dataset_version=demo.version,
            )
        )
        db.add(
            Project(
                name="Demo Road Upgrade (synthetic)",
                sector="roads",
                status="ongoing",
                location_id=town.id,
                dataset_version=demo.version,
            )
        )

        db.commit()
        print("Seed complete: 1 dataset, 4 users, 2 locations, 1 cluster, 1 asset, 1 demo project")
        print("All rows are SYNTHETIC (FR-057).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed()
    except Exception as exc:  # pragma: no cover
        print(f"Seed failed: {exc}", file=sys.stderr)
        print("Hint: run `make db-up db-migrate` first.", file=sys.stderr)
        sys.exit(1)
