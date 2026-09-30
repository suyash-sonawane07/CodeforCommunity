"""Comprehensive SYNTHETIC seed data for CivicPulse — Code for Communities 2.0 Track 1.

Populates users, locations, public datasets, infrastructure assets, demographics,
projects, citizen requests, clusters, members, gap analyses, evidence, and audit logs.
All rows are SYNTHETIC (FR-057).
"""

from __future__ import annotations

import sys

from geoalchemy2 import WKTElement

from app.db.session import SessionLocal
from app.models import (
    AuditLog,
    CitizenRequest,
    ClusterMember,
    DemographicIndicator,
    EvidenceRecord,
    ExtractedEntity,
    GapAnalysis,
    InfrastructureAsset,
    Location,
    NeedsCluster,
    PriorityFactor,
    Project,
    PublicDataset,
    RequestTranscription,
    ReviewAction,
    User,
)

SYNTHETIC_LABEL = "SYNTHETIC — not real data (FR-057)"


def seed() -> None:
    db = SessionLocal()
    try:
        # Check if already seeded with full dataset
        if db.query(CitizenRequest).count() > 0:
            print("Seed already applied — skipping.")
            return

        # --- 1. Dataset registry ------------------------------------------------
        ds_demo = (
            db.query(PublicDataset).filter(PublicDataset.name == "civicpulse_demo_seed").first()
        )
        if not ds_demo:
            ds_demo = PublicDataset(
                name="civicpulse_demo_seed",
                source_label="synthetic",
                version="synthetic_v0.1",
                description=SYNTHETIC_LABEL,
            )
            db.add(ds_demo)
            db.flush()

        # --- 2. Users (PRD §5) --------------------------------------------------
        if db.query(User).count() == 0:
            for name, email, role in [
                ("Demo Analyst", "analyst@civicpulse.dev", "analyst"),
                ("Demo Reviewer", "reviewer@civicpulse.dev", "reviewer"),
                ("Demo Decision-Maker", "decision@civicpulse.dev", "decision_maker"),
                ("Demo Admin", "admin@civicpulse.dev", "admin"),
            ]:
                db.add(User(name=name, email=email, role=role))
            db.flush()

        reviewer = db.query(User).filter(User.role == "reviewer").first()
        reviewer_id = reviewer.id if reviewer else None

        # --- 3. Locations (PostGIS geometry) ------------------------------------
        village1 = db.query(Location).filter(Location.village_ward == "Demo Village 1").first()
        if not village1:
            village1 = Location(
                state="Demo State",
                district="Demo District 1",
                block="Demo Block A",
                village_ward="Demo Village 1",
                latitude=19.876,
                longitude=75.343,
                geom=WKTElement("POINT(75.343 19.876)", srid=4326),
                confidence=0.85,
                resolution_method="gazetteer_exact",
                source_text="Demo Village 1, Demo Block A",
                status="resolved",
            )
            db.add(village1)
            db.flush()

        town2 = db.query(Location).filter(Location.village_ward == "Demo Town 2").first()
        if not town2:
            town2 = Location(
                state="Demo State",
                district="Demo District 2",
                block="Demo Block B",
                village_ward="Demo Town 2",
                latitude=19.990,
                longitude=75.180,
                geom=WKTElement("POINT(75.180 19.990)", srid=4326),
                confidence=0.82,
                resolution_method="gazetteer_exact",
                source_text="Demo Town 2, Demo Block B",
                status="resolved",
            )
            db.add(town2)
            db.flush()

        # Unresolved location for testing FR-033
        unresolved_loc = Location(
            source_text="Near the old broken bridge, unknown sector",
            latitude=None,
            longitude=None,
            geom=None,
            confidence=0.20,
            resolution_method="unresolved_text",
            status="location_unresolved",
            uncertainty_notes="Insufficient landmarks to identify administrative block.",
        )
        db.add(unresolved_loc)
        db.flush()

        # --- 4. Demographics ----------------------------------------------------
        if (
            db.query(DemographicIndicator)
            .filter(DemographicIndicator.location_id == town2.id)
            .count()
            == 0
        ):
            db.add(
                DemographicIndicator(
                    location_id=town2.id,
                    population=8600,
                    deprivation_index=0.31,
                    dataset_version=ds_demo.version,
                    indicator_name="census_proxy",
                )
            )

        # --- 5. Infrastructure Assets -------------------------------------------
        school = (
            db.query(InfrastructureAsset).filter(InfrastructureAsset.asset_type == "school").first()
        )
        if not school:
            db.add(
                InfrastructureAsset(
                    asset_type="school",
                    name="Demo Village School (synthetic)",
                    location_id=village1.id,
                    dataset_version=ds_demo.version,
                    attributes='{"facilities": ["classroom"], "facilities_note": "no functional toilet block"}',
                )
            )

        water_point = (
            db.query(InfrastructureAsset)
            .filter(InfrastructureAsset.asset_type == "water_point")
            .first()
        )
        if not water_point:
            db.add(
                InfrastructureAsset(
                    asset_type="water_point",
                    name="Demo Village Water Point (synthetic)",
                    location_id=village1.id,
                    dataset_version=ds_demo.version,
                    attributes='{"functional": true, "hours_per_day": 2}',
                )
            )

        # --- 6. Projects --------------------------------------------------------
        health_proj = db.query(Project).filter(Project.sector == "health").first()
        if not health_proj:
            db.add(
                Project(
                    name="Demo Health Sub-centre Renovation (synthetic)",
                    sector="health",
                    status="sanctioned",
                    location_id=village1.id,
                    dataset_version=ds_demo.version,
                    description="Sanctioned renovation, exact siting not yet fixed.",
                )
            )

        # --- 7. Citizen Requests (Multilingual: Hindi, Marathi, English) --------
        req1 = CitizenRequest(
            reference_code="CP-2026-004821",
            channel="text",
            raw_text="गाँव में शाम 5 बजे के बाद बस नहीं मिलती।",
            language="hi",
            status="active",
            consent_ack=True,
            uncertainty_notes=["Verified text submission"],
            source="web",
        )
        req2 = CitizenRequest(
            reference_code="CP-2026-004822",
            channel="text",
            raw_text="शाळेत शौचालय नाही, मुलांना अडचण येते.",
            language="mr",
            status="active",
            consent_ack=True,
            uncertainty_notes=["Verified text submission"],
            source="web",
        )
        req3 = CitizenRequest(
            reference_code="CP-2026-004823",
            channel="voice",
            raw_text="Water supply comes only two hours a week.",
            language="en",
            transcript="Water supply comes only two hours a week.",
            status="active",
            consent_ack=True,
            audio_url="/static/audio/water_issue.wav",
            uncertainty_notes=["Transcribed voice submission via STT"],
            source="web",
        )
        req4 = CitizenRequest(
            reference_code="CP-2026-004824",
            channel="text",
            raw_text="The road near the old temple is broken.",
            language="en",
            status="received",
            consent_ack=True,
            uncertainty_notes=["Unresolved location queued for analyst review"],
            source="web",
        )
        db.add_all([req1, req2, req3, req4])
        db.flush()

        # Transcriptions & Entities
        db.add(
            RequestTranscription(
                request_id=req3.id,
                stt_model="whisper-base",
                stt_provider="whisper",
                confidence=0.89,
                transcript="Water supply comes only two hours a week.",
            )
        )
        db.add_all(
            [
                ExtractedEntity(
                    request_id=req1.id, entity_type="facility", value="bus_stop", confidence=0.88
                ),
                ExtractedEntity(
                    request_id=req1.id, entity_type="time", value="after 5 pm", confidence=0.90
                ),
                ExtractedEntity(
                    request_id=req2.id, entity_type="facility", value="school", confidence=0.92
                ),
                ExtractedEntity(
                    request_id=req2.id, entity_type="facility", value="toilet", confidence=0.95
                ),
                ExtractedEntity(
                    request_id=req3.id, entity_type="facility", value="water_point", confidence=0.85
                ),
            ]
        )

        # --- 8. Needs Clusters & Members ----------------------------------------
        # Cluster 1: Transport Access (Demo Village 1)
        cl1 = db.query(NeedsCluster).filter(NeedsCluster.id == 1).first()
        if not cl1:
            cl1 = NeedsCluster(
                issue_type="transport",
                status="active",
                review_status="approved",
                independent_demand_count=7,
                raw_message_count=12,
                location_id=village1.id,
                uncertainty_notes=["High confidence clustering from 12 regional citizen reports."],
                dataset_version=ds_demo.version,
            )
            db.add(cl1)
            db.flush()
        else:
            cl1.status = "active"
            cl1.review_status = "approved"
            cl1.independent_demand_count = 7
            cl1.raw_message_count = 12

        db.add(
            ClusterMember(
                cluster_id=cl1.id, request_id=req1.id, similarity_score=0.92, assignment="auto"
            )
        )

        # Cluster 2: Education Sanitation (Demo Village 1)
        cl2 = NeedsCluster(
            issue_type="education",
            status="active",
            review_status="pending",
            independent_demand_count=5,
            raw_message_count=8,
            location_id=village1.id,
            uncertainty_notes=["School sanitation deficiency reported by multiple parents."],
            dataset_version=ds_demo.version,
        )
        db.add(cl2)
        db.flush()
        db.add(
            ClusterMember(
                cluster_id=cl2.id, request_id=req2.id, similarity_score=0.95, assignment="auto"
            )
        )

        # Cluster 3: Water Supply (Demo Town 2)
        cl3 = NeedsCluster(
            issue_type="water",
            status="active",
            review_status="needs_more_evidence",
            independent_demand_count=9,
            raw_message_count=15,
            location_id=town2.id,
            uncertainty_notes=["Intermittent water supply reported; pressure check needed."],
            dataset_version=ds_demo.version,
        )
        db.add(cl3)
        db.flush()
        db.add(
            ClusterMember(
                cluster_id=cl3.id, request_id=req3.id, similarity_score=0.89, assignment="auto"
            )
        )

        # Cluster 4: Roads (Unresolved location)
        cl4 = NeedsCluster(
            issue_type="roads",
            status="forming",
            review_status="pending",
            independent_demand_count=1,
            raw_message_count=1,
            location_id=unresolved_loc.id,
            uncertainty_notes=["Location unresolved — pending human geocoding (FR-033)."],
            dataset_version=ds_demo.version,
        )
        db.add(cl4)
        db.flush()
        db.add(
            ClusterMember(
                cluster_id=cl4.id, request_id=req4.id, similarity_score=1.0, assignment="auto"
            )
        )

        # --- 9. Evidence & Gap Analysis Records ---------------------------------
        for cl in [cl1, cl2, cl3]:
            db.add(
                GapAnalysis(
                    cluster_id=cl.id,
                    gap_found=True,
                    benchmark_used="National Public Infrastructure Accessibility Standard",
                    demand_summary=f"{cl.independent_demand_count} verified citizen reports indicating unmet service.",
                    gap_summary="Nearest functional facility is outside standard service distance.",
                    recommendation_summary=f"Recommend capital allocation for {cl.issue_type} enhancement.",
                    uncertainty_notes=[
                        "Synthetically verified against public infrastructure layer."
                    ],
                )
            )
            db.add(
                PriorityFactor(
                    cluster_id=cl.id,
                    demand=0.75,
                    gap=0.80,
                    impact=0.65,
                    equity_adj=1.25,
                    weights={"demand": 0.25, "gap": 0.25, "impact": 0.25, "equity": 0.25},
                    priority_index=0.4875,
                    is_incomplete=False,
                )
            )
            db.add(
                EvidenceRecord(
                    cluster_id=cl.id,
                    payload={"cluster_id": cl.id, "verified": True},
                    source="system",
                )
            )

        # --- 10. Review Actions & Audit Trail -----------------------------------
        db.add(
            ReviewAction(
                cluster_id=cl1.id,
                reviewer_id=reviewer_id,
                action="approve",
                note="Verified through population density and lack of bus stop within 6km. Approved for planning.",
                before_value={"status": "forming"},
                after_value={"status": "active", "review_status": "approved"},
            )
        )
        db.add(
            AuditLog(
                actor_id=reviewer_id,
                action="CLUSTER_REVIEW_APPROVE",
                entity_type="needs_clusters",
                entity_id=cl1.id,
                before_value={"status": "forming"},
                after_value={"status": "active", "review_status": "approved"},
                detail={"note": "Approved for priority planning intervention"},
            )
        )

        db.commit()
        print("Comprehensive seed completed successfully!")
        print(
            "Seeded: 4 users, 3 locations, 4 citizen requests (hi, mr, en), 4 clusters, assets, projects, gap analyses, evidence, and audit logs."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed()
    except Exception as exc:
        print(f"Seed failed: {exc}", file=sys.stderr)
        sys.exit(1)
