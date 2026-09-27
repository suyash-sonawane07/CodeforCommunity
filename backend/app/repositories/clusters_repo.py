"""Repository for NeedsCluster and ClusterMember entities."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session, joinedload

from app.models import ClusterMember, Location, NeedsCluster


class ClusterRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_clusters(
        self,
        issue_type: Optional[str] = None,
        district: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[NeedsCluster]:
        query = self.db.query(NeedsCluster)
        if issue_type:
            query = query.filter(NeedsCluster.issue_type == issue_type)
        if status:
            query = query.filter(NeedsCluster.status == status)
        if district:
            query = query.join(Location, NeedsCluster.location_id == Location.id, isouter=True).filter(
                Location.district.ilike(f"%{district}%")
            )
        return query.order_by(NeedsCluster.id.asc()).all()

    def get_by_id(self, cluster_id: int) -> Optional[NeedsCluster]:
        return (
            self.db.query(NeedsCluster)
            .options(joinedload(NeedsCluster.members))
            .filter(NeedsCluster.id == cluster_id)
            .first()
        )

    def create_cluster(
        self,
        issue_type: str,
        location_id: Optional[int] = None,
        status: str = "forming",
        independent_demand_count: int = 1,
        raw_message_count: int = 1,
        uncertainty_notes: Optional[list] = None,
        dataset_version: Optional[str] = "synthetic_v0.1",
    ) -> NeedsCluster:
        cluster = NeedsCluster(
            issue_type=issue_type,
            location_id=location_id,
            status=status,
            independent_demand_count=independent_demand_count,
            raw_message_count=raw_message_count,
            uncertainty_notes=uncertainty_notes or [],
            dataset_version=dataset_version,
        )
        self.db.add(cluster)
        self.db.flush()
        return cluster

    def update_cluster(
        self,
        cluster_id: int,
        issue_type: Optional[str] = None,
        status: Optional[str] = None,
        review_status: Optional[str] = None,
        location_id: Optional[int] = None,
        uncertainty_notes: Optional[list] = None,
    ) -> Optional[NeedsCluster]:
        cluster = self.get_by_id(cluster_id)
        if not cluster:
            return None
        if issue_type is not None:
            cluster.issue_type = issue_type
        if status is not None:
            cluster.status = status
        if review_status is not None:
            cluster.review_status = review_status
        if location_id is not None:
            cluster.location_id = location_id
        if uncertainty_notes is not None:
            cluster.uncertainty_notes = uncertainty_notes
        self.db.flush()
        return cluster

    def add_member(
        self,
        cluster_id: int,
        request_id: int,
        similarity_score: Optional[float] = None,
        assignment: str = "auto",
    ) -> ClusterMember:
        member = ClusterMember(
            cluster_id=cluster_id,
            request_id=request_id,
            similarity_score=similarity_score,
            assignment=assignment,
        )
        self.db.add(member)

        # Update counts
        cluster = self.get_by_id(cluster_id)
        if cluster:
            cluster.raw_message_count += 1
            # Simple deduplication heuristic: count independent demand
            cluster.independent_demand_count = max(1, cluster.raw_message_count - 1 if cluster.raw_message_count > 2 else cluster.raw_message_count)

        self.db.flush()
        return member

    def find_matching_cluster(
        self, issue_type: str, location_id: Optional[int] = None
    ) -> Optional[NeedsCluster]:
        """Find an existing active or forming cluster with matching sector and location."""
        query = self.db.query(NeedsCluster).filter(
            NeedsCluster.issue_type == issue_type,
            NeedsCluster.status.in_(["forming", "active"]),
        )
        if location_id:
            query = query.filter(NeedsCluster.location_id == location_id)
        return query.first()
