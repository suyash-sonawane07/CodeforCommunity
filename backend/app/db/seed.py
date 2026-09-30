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


def _seed_base_demo(db) -> None:

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

        
        from app.core.security import get_password_hash
        # --- 2. Users (PRD §5) --------------------------------------------------
        if db.query(User).count() == 0:
            for name, email, role, pwd in [
                ("Demo Analyst", "analyst@civicpulse.dev", "analyst", "demo123"),
                ("Demo Reviewer", "reviewer@civicpulse.dev", "reviewer", "demo123"),
                ("Demo Decision-Maker", "decision@civicpulse.dev", "decision_maker", "demo123"),
                ("Demo Admin", "admin@civicpulse.dev", "admin", "demo123"),
                ("Demo User", "user@demo.com", "user", "demo123"),
                ("Demo Supervisor", "supervisor@demo.com", "supervisor", "demo123"),
            ]:
                db.add(User(name=name, email=email, role=role, hashed_password=get_password_hash(pwd)))
            db.flush()
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
        reviewer_user = (
            db.query(User).filter(User.email == "reviewer@civicpulse.dev").first()
            or db.query(User).filter(User.role == "reviewer").first()
            or db.query(User).first()
        )
        reviewer_id = reviewer_user.id if reviewer_user else None

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
        print("Base demo seed completed successfully!")


def _seed_brics_datasets(db) -> None:
    """Seeds realistic synthetic datasets, locations, assets, demographics, and projects
    for 3 BRICS countries: India, Brazil, and South Africa (FR-057).
    """
    # --- 1. Dataset registry ---
    ds_ind = db.query(PublicDataset).filter(PublicDataset.name == "india_census_infrastructure_synthetic").first()
    if not ds_ind:
        ds_ind = PublicDataset(
            name="india_census_infrastructure_synthetic",
            source_label="synthetic",
            version="ind_v2026_synth",
            description="SYNTHETIC — not real data (FR-057): India Census 2021 & Jal Jeevan Mission / PMGSY Proxy",
        )
        db.add(ds_ind)

    ds_bra = db.query(PublicDataset).filter(PublicDataset.name == "brazil_ibge_censo_synthetic").first()
    if not ds_bra:
        ds_bra = PublicDataset(
            name="brazil_ibge_censo_synthetic",
            source_label="synthetic",
            version="bra_v2026_synth",
            description="SYNTHETIC — not real data (FR-057): IBGE Censo Demográfico 2022 & SNIS Saneamento Básico Proxy",
        )
        db.add(ds_bra)

    ds_zaf = db.query(PublicDataset).filter(PublicDataset.name == "south_africa_statssa_synthetic").first()
    if not ds_zaf:
        ds_zaf = PublicDataset(
            name="south_africa_statssa_synthetic",
            source_label="synthetic",
            version="zaf_v2026_synth",
            description="SYNTHETIC — not real data (FR-057): Stats SA Community Survey & MIG Proxy",
        )
        db.add(ds_zaf)
    db.flush()

    # --- 2. Locations ---
    loc_paithan = db.query(Location).filter(Location.village_ward == "Paithan Rural Hub").first()
    if not loc_paithan:
        loc_paithan = Location(
            state="Maharashtra",
            district="Chhatrapati Sambhajinagar",
            block="Paithan",
            village_ward="Paithan Rural Hub",
            latitude=19.479,
            longitude=75.383,
            geom=WKTElement("POINT(75.383 19.479)", srid=4326),
            confidence=0.92,
            resolution_method="gazetteer_exact",
            source_text="Paithan Rural Hub, Paithan",
            status="resolved",
        )
        db.add(loc_paithan)

    loc_shirur = db.query(Location).filter(Location.village_ward == "Shirur Rural Ward").first()
    if not loc_shirur:
        loc_shirur = Location(
            state="Maharashtra",
            district="Pune",
            block="Shirur",
            village_ward="Shirur Rural Ward",
            latitude=18.825,
            longitude=74.378,
            geom=WKTElement("POINT(74.378 18.825)", srid=4326),
            confidence=0.90,
            resolution_method="gazetteer_exact",
            source_text="Shirur Rural Ward, Pune",
            status="resolved",
        )
        db.add(loc_shirur)

    loc_mare = db.query(Location).filter(Location.village_ward == "Favela da Maré").first()
    if not loc_mare:
        loc_mare = Location(
            state="Rio de Janeiro",
            district="Zona Norte",
            block="Complexo da Maré",
            village_ward="Favela da Maré",
            latitude=-22.861,
            longitude=-43.245,
            geom=WKTElement("POINT(-43.245 -22.861)", srid=4326),
            confidence=0.88,
            resolution_method="gazetteer_exact",
            source_text="Favela da Maré, Zona Norte, Rio de Janeiro",
            status="resolved",
        )
        db.add(loc_mare)

    loc_santos = db.query(Location).filter(Location.village_ward == "Santos Encosta").first()
    if not loc_santos:
        loc_santos = Location(
            state="São Paulo",
            district="Baixada Santista",
            block="Morros",
            village_ward="Santos Encosta",
            latitude=-23.953,
            longitude=-46.332,
            geom=WKTElement("POINT(-46.332 -23.953)", srid=4326),
            confidence=0.86,
            resolution_method="gazetteer_exact",
            source_text="Santos Encosta, Morros, Santos",
            status="resolved",
        )
        db.add(loc_santos)

    loc_soweto = db.query(Location).filter(Location.village_ward == "Soweto Ward 42").first()
    if not loc_soweto:
        loc_soweto = Location(
            state="Gauteng",
            district="City of Johannesburg",
            block="Region D",
            village_ward="Soweto Ward 42",
            latitude=-26.267,
            longitude=27.858,
            geom=WKTElement("POINT(27.858 -26.267)", srid=4326),
            confidence=0.89,
            resolution_method="gazetteer_exact",
            source_text="Soweto Ward 42, Region D, Johannesburg",
            status="resolved",
        )
        db.add(loc_soweto)

    loc_khaye = db.query(Location).filter(Location.village_ward == "Khayelitsha Site C").first()
    if not loc_khaye:
        loc_khaye = Location(
            state="Western Cape",
            district="City of Cape Town",
            block="Khayelitsha",
            village_ward="Khayelitsha Site C",
            latitude=-34.038,
            longitude=18.665,
            geom=WKTElement("POINT(18.665 -34.038)", srid=4326),
            confidence=0.87,
            resolution_method="gazetteer_exact",
            source_text="Khayelitsha Site C, Cape Town",
            status="resolved",
        )
        db.add(loc_khaye)
    db.flush()

    # --- 3. Demographics ---
    demos = [
        (loc_paithan.id, 12500, 0.74, "ind_v2026_synth", "Census 2021 Proxy: Socio-Economic Vulnerability Index"),
        (loc_shirur.id, 8200, 0.45, "ind_v2026_synth", "Census 2021 Proxy: Rural Accessibility Index"),
        (loc_mare.id, 24000, 0.82, "bra_v2026_synth", "IBGE Censo 2022 Proxy: Índice de Vulnerabilidade Social (IVS)"),
        (loc_santos.id, 11500, 0.58, "bra_v2026_synth", "IBGE Censo 2022 Proxy: Vulnerabilidade Habitacional"),
        (loc_soweto.id, 31000, 0.76, "zaf_v2026_synth", "Stats SA Multidimensional Poverty Index (SAMPI)"),
        (loc_khaye.id, 19800, 0.85, "zaf_v2026_synth", "Stats SA Informal Settlements Deprivation Index"),
    ]
    for loc_id, pop, dep_idx, v, ind_name in demos:
        if db.query(DemographicIndicator).filter(DemographicIndicator.location_id == loc_id).count() == 0:
            db.add(
                DemographicIndicator(
                    location_id=loc_id,
                    population=pop,
                    deprivation_index=dep_idx,
                    dataset_version=v,
                    indicator_name=ind_name,
                )
            )
    db.flush()

    # --- 4. Infrastructure Assets ---
    assets = [
        ("water_point", "Paithan Habitation Handpump (synthetic)", loc_paithan.id, "ind_v2026_synth", '{"functional": false, "issue": "dry borewell", "capacity_lpcd": 15, "source_label": "SYNTHETIC"}'),
        ("power_substation", "Paithan 11kV Rural Substation (synthetic)", loc_paithan.id, "ind_v2026_synth", '{"operational": true, "voltage": "11kV", "source_label": "SYNTHETIC"}'),
        ("school", "Shirur Zilla Parishad Primary School (synthetic)", loc_shirur.id, "ind_v2026_synth", '{"classrooms": 6, "functional_toilets": 0, "enrolment": 240, "source_label": "SYNTHETIC"}'),
        ("clinic", "Shirur Primary Health Centre (synthetic)", loc_shirur.id, "ind_v2026_synth", '{"type": "phc", "beds": 6, "source_label": "SYNTHETIC"}'),
        ("drainage_point", "Canal do Cunha Drainage Outfall (synthetic)", loc_mare.id, "bra_v2026_synth", '{"functional": false, "overflow_risk": "critical", "source_label": "SYNTHETIC"}'),
        ("clinic", "Clínica da Família Jeremias (synthetic)", loc_mare.id, "bra_v2026_synth", '{"type": "primary_care", "capacity_daily": 150, "source_label": "SYNTHETIC"}'),
        ("bus_stop", "Parada Linha 13 Morro São Bento (synthetic)", loc_santos.id, "bra_v2026_synth", '{"frequency_mins": 60, "shelter": false, "source_label": "SYNTHETIC"}'),
        ("power_substation", "Orlando East Feeder Substation (synthetic)", loc_soweto.id, "zaf_v2026_synth", '{"overloaded": true, "capacity_mva": 5.0, "source_label": "SYNTHETIC"}'),
        ("clinic", "Mofolo Community Health Centre (synthetic)", loc_soweto.id, "zaf_v2026_synth", '{"type": "chc", "beds": 20, "source_label": "SYNTHETIC"}'),
        ("water_point", "Site C Standpipe Cluster 4 (synthetic)", loc_khaye.id, "zaf_v2026_synth", '{"taps_functional": 2, "taps_broken": 4, "source_label": "SYNTHETIC"}'),
        ("school", "Khayelitsha Secondary School (synthetic)", loc_khaye.id, "zaf_v2026_synth", '{"classrooms": 18, "toilets_functional": 4, "source_label": "SYNTHETIC"}'),
    ]
    for atype, aname, loc_id, v, attrs in assets:
        if db.query(InfrastructureAsset).filter(InfrastructureAsset.name == aname).count() == 0:
            db.add(
                InfrastructureAsset(
                    asset_type=atype,
                    name=aname,
                    location_id=loc_id,
                    dataset_version=v,
                    attributes=attrs,
                )
            )
    db.flush()

    # --- 5. Projects ---
    projects = [
        ("Jal Jeevan Mission Paithan Piped Water Scheme", "water", "ongoing", loc_paithan.id, "ind_v2026_synth", "Ongoing piped drinking water distribution network (synthetic)."),
        ("PMGSY Shirur Feeder Road Package", "roads", "completed", loc_shirur.id, "ind_v2026_synth", "Completed PMGSY all-weather rural road (synthetic)."),
        ("PAC Saneamento Básico e Drenagem Maré", "sanitation", "sanctioned", loc_mare.id, "bra_v2026_synth", "Sanctioned municipal drainage and canal clearing program (synthetic)."),
        ("Eskom Soweto Substation Infrastructure Upgrade", "power", "ongoing", loc_soweto.id, "zaf_v2026_synth", "Ongoing transformer replacement and loadshedding mitigation (synthetic)."),
    ]
    for pname, sec, st, loc_id, v, desc in projects:
        if db.query(Project).filter(Project.name == pname).count() == 0:
            db.add(
                Project(
                    name=pname,
                    sector=sec,
                    status=st,
                    location_id=loc_id,
                    dataset_version=v,
                    description=desc,
                )
            )
    db.flush()

    # --- 6. Citizen Requests & Needs Clusters ---
    if not db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-IND001").first():
        req_ind = CitizenRequest(
            reference_code="CP-2026-IND001",
            channel="text",
            raw_text="पैठण गावात गेल्या १५ दिवसांपासून नळाला पाणी नाही, टँकर सुद्धा वेळेवर येत नाही.",
            language="mr",
            status="active",
            consent_ack=True,
            uncertainty_notes=["Verified Marathi text submission from Paithan (FR-057)"],
            source="web",
        )
        db.add(req_ind)
        db.flush()

        cl_ind = NeedsCluster(
            issue_type="water",
            status="active",
            review_status="pending",
            independent_demand_count=14,
            raw_message_count=22,
            location_id=loc_paithan.id,
            uncertainty_notes=["High demand concentration in Paithan drinking water grid."],
            dataset_version="ind_v2026_synth",
        )
        db.add(cl_ind)
        db.flush()
        db.add(ClusterMember(cluster_id=cl_ind.id, request_id=req_ind.id, similarity_score=0.94, assignment="auto"))

    if not db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-BRA001").first():
        req_bra = CitizenRequest(
            reference_code="CP-2026-BRA001",
            channel="text",
            raw_text="O canal da Maré transborda a cada chuva forte e a água suja invade as casas na rua principal.",
            language="pt",
            status="active",
            consent_ack=True,
            uncertainty_notes=["Verified Portuguese text submission from Favela da Maré (FR-057)"],
            source="web",
        )
        db.add(req_bra)
        db.flush()

        cl_bra = NeedsCluster(
            issue_type="sanitation",
            status="active",
            review_status="pending",
            independent_demand_count=18,
            raw_message_count=31,
            location_id=loc_mare.id,
            uncertainty_notes=["Recurrent drainage overflow and sewage flooding reports in Maré."],
            dataset_version="bra_v2026_synth",
        )
        db.add(cl_bra)
        db.flush()
        db.add(ClusterMember(cluster_id=cl_bra.id, request_id=req_bra.id, similarity_score=0.96, assignment="auto"))

    if not db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-ZAF001").first():
        req_zaf = CitizenRequest(
            reference_code="CP-2026-ZAF001",
            channel="text",
            raw_text="Frequent transformer explosions in Ward 42 leave the community and local clinic without power for days.",
            language="en",
            status="active",
            consent_ack=True,
            uncertainty_notes=["Verified English text submission from Soweto (FR-057)"],
            source="web",
        )
        db.add(req_zaf)
        db.flush()

        cl_zaf = NeedsCluster(
            issue_type="power",
            status="active",
            review_status="pending",
            independent_demand_count=16,
            raw_message_count=25,
            location_id=loc_soweto.id,
            uncertainty_notes=["Persistent distribution substation failure reported by residents and health centre."],
            dataset_version="zaf_v2026_synth",
        )
        db.add(cl_zaf)
        db.flush()
        db.add(ClusterMember(cluster_id=cl_zaf.id, request_id=req_zaf.id, similarity_score=0.91, assignment="auto"))

    if not db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-ZAF002").first():
        req_zaf2 = CitizenRequest(
            reference_code="CP-2026-ZAF002",
            channel="text",
            raw_text="Only two working water standpipes in Site C for over a thousand families, queues start at 4am.",
            language="en",
            status="active",
            consent_ack=True,
            uncertainty_notes=["Verified English text submission from Khayelitsha (FR-057)"],
            source="web",
        )
        db.add(req_zaf2)
        db.flush()

        cl_zaf2 = NeedsCluster(
            issue_type="water",
            status="active",
            review_status="approved",
            independent_demand_count=12,
            raw_message_count=19,
            location_id=loc_khaye.id,
            uncertainty_notes=["Informal settlement communal standpipe deficit; queue times exceed 2 hours."],
            dataset_version="zaf_v2026_synth",
        )
        db.add(cl_zaf2)
        db.flush()
        db.add(ClusterMember(cluster_id=cl_zaf2.id, request_id=req_zaf2.id, similarity_score=0.93, assignment="auto"))

    db.commit()
    print("BRICS Synthetic datasets (India, Brazil, South Africa) seeded successfully!")


def seed() -> None:
    db = SessionLocal()
    try:
        base_seeded = (
            db.query(CitizenRequest).filter(CitizenRequest.reference_code == "CP-2026-004821").first()
            is not None
        )
        if not base_seeded:
            _seed_base_demo(db)
        _seed_brics_datasets(db)
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
