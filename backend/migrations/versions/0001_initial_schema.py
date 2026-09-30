"""initial schema — PostGIS extension + all 18 PRD §9.1 entities

Revision ID: 0001
Revises:
Create Date: 2026-09-27

SCAFFOLD: skeleton tables per PRD §9.1. Confidence/source/dataset_version/
review_status/uncertainty_notes columns are present from day one (brief §25).
"""

import sqlalchemy as sa
from alembic import op
from geoalchemy2 import Geometry

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

# (table name → columns) created in FK-dependency order.
created_at = sa.Column(
    "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
)


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis")

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=True),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        created_at,
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "locations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("state", sa.String(length=100), nullable=True),
        sa.Column("district", sa.String(length=100), nullable=True),
        sa.Column("block", sa.String(length=100), nullable=True),
        sa.Column("village_ward", sa.String(length=150), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("geom", Geometry(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("resolution_method", sa.String(length=50), nullable=True),
        sa.Column("source_text", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("uncertainty_notes", sa.Text(), nullable=True),
        created_at,
    )
    op.create_index("ix_locations_geom", "locations", ["geom"], postgresql_using="gist")

    op.create_table(
        "citizen_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("reference_code", sa.String(length=30), nullable=False),
        sa.Column("channel", sa.String(length=10), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        sa.Column("audio_url", sa.String(length=500), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("consent_ack", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("review_status", sa.String(length=30), nullable=True),
        sa.Column("uncertainty_notes", sa.JSON(), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=False),
        created_at,
    )
    op.create_index(
        op.f("ix_citizen_requests_reference_code"),
        "citizen_requests",
        ["reference_code"],
        unique=True,
    )

    op.create_table(
        "request_transcriptions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("citizen_requests.id"), nullable=False),
        sa.Column("stt_model", sa.String(length=100), nullable=False),
        sa.Column("stt_provider", sa.String(length=50), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        created_at,
    )
    op.create_index(
        op.f("ix_request_transcriptions_request_id"), "request_transcriptions", ["request_id"]
    )

    op.create_table(
        "extracted_entities",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("citizen_requests.id"), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("extraction_version", sa.String(length=50), nullable=True),
        created_at,
    )
    op.create_index(op.f("ix_extracted_entities_request_id"), "extracted_entities", ["request_id"])

    op.create_table(
        "public_datasets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("source_label", sa.String(length=20), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("ingested_at", sa.String(length=30), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        created_at,
    )
    op.create_index(op.f("ix_public_datasets_name"), "public_datasets", ["name"], unique=True)

    op.create_table(
        "infrastructure_assets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("asset_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("dataset_version", sa.String(length=50), nullable=False),
        sa.Column("attributes", sa.Text(), nullable=True),
        created_at,
    )
    op.create_index(
        op.f("ix_infrastructure_assets_asset_type"), "infrastructure_assets", ["asset_type"]
    )

    op.create_table(
        "demographic_indicators",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("population", sa.Integer(), nullable=True),
        sa.Column("deprivation_index", sa.Float(), nullable=True),
        sa.Column("dataset_version", sa.String(length=50), nullable=False),
        sa.Column("indicator_name", sa.String(length=100), nullable=True),
        created_at,
    )

    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("sector", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("dataset_version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        created_at,
    )
    op.create_index(op.f("ix_projects_sector"), "projects", ["sector"])

    op.create_table(
        "needs_clusters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("issue_type", sa.String(length=50), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        sa.Column("review_status", sa.String(length=30), nullable=True),
        sa.Column("independent_demand_count", sa.Integer(), nullable=False),
        sa.Column("raw_message_count", sa.Integer(), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("locations.id"), nullable=True),
        sa.Column("time_window_start", sa.String(length=30), nullable=True),
        sa.Column("time_window_end", sa.String(length=30), nullable=True),
        sa.Column("uncertainty_notes", sa.JSON(), nullable=True),
        sa.Column("dataset_version", sa.String(length=50), nullable=True),
        created_at,
    )
    op.create_index(op.f("ix_needs_clusters_issue_type"), "needs_clusters", ["issue_type"])
    op.create_index(op.f("ix_needs_clusters_status"), "needs_clusters", ["status"])
    op.create_index(op.f("ix_needs_clusters_location_id"), "needs_clusters", ["location_id"])

    op.create_table(
        "cluster_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("needs_clusters.id"), nullable=False),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("citizen_requests.id"), nullable=False),
        sa.Column("similarity_score", sa.Float(), nullable=True),
        sa.Column("assignment", sa.String(length=20), nullable=False),
        created_at,
    )
    op.create_index(op.f("ix_cluster_members_cluster_id"), "cluster_members", ["cluster_id"])
    op.create_index(op.f("ix_cluster_members_request_id"), "cluster_members", ["request_id"])

    op.create_table(
        "gap_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("needs_clusters.id"), nullable=False),
        sa.Column("gap_found", sa.Boolean(), nullable=False),
        sa.Column("benchmark_used", sa.String(length=200), nullable=True),
        sa.Column(
            "conflicting_project_id", sa.Integer(), sa.ForeignKey("projects.id"), nullable=True
        ),
        sa.Column("demand_summary", sa.Text(), nullable=True),
        sa.Column("gap_summary", sa.Text(), nullable=True),
        sa.Column("recommendation_summary", sa.Text(), nullable=True),
        sa.Column("uncertainty_notes", sa.JSON(), nullable=True),
        created_at,
    )
    op.create_index(op.f("ix_gap_analyses_cluster_id"), "gap_analyses", ["cluster_id"])

    op.create_table(
        "priority_factors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("needs_clusters.id"), nullable=False),
        sa.Column("demand", sa.Float(), nullable=True),
        sa.Column("gap", sa.Float(), nullable=True),
        sa.Column("impact", sa.Float(), nullable=True),
        sa.Column("equity_adj", sa.Float(), nullable=True),
        sa.Column("weights", sa.JSON(), nullable=True),
        sa.Column("priority_index", sa.Float(), nullable=True),
        sa.Column("is_incomplete", sa.Boolean(), nullable=False),
        created_at,
    )
    op.create_index(op.f("ix_priority_factors_cluster_id"), "priority_factors", ["cluster_id"])

    op.create_table(
        "evidence_records",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("needs_clusters.id"), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=True),
        sa.Column("generated_at", sa.String(length=30), nullable=True),
        sa.Column("generator_version", sa.String(length=50), nullable=True),
        sa.Column("source", sa.String(length=30), nullable=False),
        created_at,
    )
    op.create_index(op.f("ix_evidence_records_cluster_id"), "evidence_records", ["cluster_id"])

    op.create_table(
        "simulation_scenarios",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("sector_allocations", sa.JSON(), nullable=True),
        sa.Column("result_payload", sa.JSON(), nullable=True),
        sa.Column("dataset_version", sa.String(length=50), nullable=True),
        created_at,
    )

    op.create_table(
        "review_actions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("needs_clusters.id"), nullable=False),
        sa.Column("reviewer_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=30), nullable=False),
        sa.Column("note", sa.Text(), nullable=False),
        sa.Column("before_value", sa.JSON(), nullable=True),
        sa.Column("after_value", sa.JSON(), nullable=True),
        created_at,
    )
    op.create_index(op.f("ix_review_actions_cluster_id"), "review_actions", ["cluster_id"])

    op.create_table(
        "interventions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("needs_clusters.id"), nullable=False),
        sa.Column("baseline_snapshot", sa.JSON(), nullable=True),
        sa.Column("followup_snapshot", sa.JSON(), nullable=True),
        sa.Column("is_synthetic", sa.Boolean(), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False),
        created_at,
    )
    op.create_index(op.f("ix_interventions_cluster_id"), "interventions", ["cluster_id"])

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("actor_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("entity_type", sa.String(length=50), nullable=True),
        sa.Column("entity_id", sa.Integer(), nullable=True),
        sa.Column("before_value", sa.JSON(), nullable=True),
        sa.Column("after_value", sa.JSON(), nullable=True),
        sa.Column("detail", sa.JSON(), nullable=True),
        created_at,
    )


def downgrade() -> None:
    for table in (
        "audit_logs",
        "interventions",
        "review_actions",
        "simulation_scenarios",
        "evidence_records",
        "priority_factors",
        "gap_analyses",
        "cluster_members",
        "needs_clusters",
        "projects",
        "demographic_indicators",
        "infrastructure_assets",
        "public_datasets",
        "extracted_entities",
        "request_transcriptions",
        "citizen_requests",
        "locations",
        "users",
    ):
        op.drop_table(table)
    # PostGIS extension intentionally left installed.
