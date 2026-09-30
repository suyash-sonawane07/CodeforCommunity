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
            query = query.join(
                Location, NeedsCluster.location_id == Location.id, isouter=True
            ).filter(Location.district.ilike(f"%{district}%"))
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

            from app.models import CitizenRequest

            new_req = self.db.query(CitizenRequest).filter(CitizenRequest.id == request_id).first()
            existing_reqs = (
                self.db.query(CitizenRequest)
                .join(ClusterMember, ClusterMember.request_id == CitizenRequest.id)
                .filter(ClusterMember.cluster_id == cluster_id, CitizenRequest.id != request_id)
                .all()
            )

            is_duplicate = False
            if new_req and existing_reqs:
                new_text = (new_req.raw_text or new_req.transcript or "").strip().lower()
                for ex in existing_reqs:
                    ex_text = (ex.raw_text or ex.transcript or "").strip().lower()
                    if new_text and ex_text and new_text == ex_text:
                        is_duplicate = True
                        break
                    if new_req.channel == ex.channel and new_req.channel in (
                        "telegram",
                        "whatsapp",
                    ):
                        if new_text and ex_text and (new_text in ex_text or ex_text in new_text):
                            is_duplicate = True
                            break

            if not is_duplicate:
                cluster.independent_demand_count += 1
            elif cluster.independent_demand_count < 1:
                cluster.independent_demand_count = 1

        self.db.flush()
        return member

    def find_matching_cluster(
        self,
        issue_type: str,
        location_id: Optional[int] = None,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        max_distance_km: float = 10.0,
    ) -> Optional[NeedsCluster]:
        """Find an existing active or forming cluster with matching sector and location/proximity."""
        # 1. Exact location_id match
        if location_id:
            exact = (
                self.db.query(NeedsCluster)
                .filter(
                    NeedsCluster.issue_type == issue_type,
                    NeedsCluster.location_id == location_id,
                    NeedsCluster.status.in_(["forming", "active"]),
                )
                .first()
            )
            if exact:
                return exact

        # 2. Proximity search if latitude/longitude provided
        if latitude is not None and longitude is not None:
            import math

            clusters_with_loc = (
                self.db.query(NeedsCluster, Location)
                .join(Location, NeedsCluster.location_id == Location.id)
                .filter(
                    NeedsCluster.issue_type == issue_type,
                    NeedsCluster.status.in_(["forming", "active"]),
                    Location.latitude.isnot(None),
                    Location.longitude.isnot(None),
                )
                .all()
            )
            for cl, loc in clusters_with_loc:
                lat1, lon1 = math.radians(latitude), math.radians(longitude)
                lat2, lon2 = math.radians(loc.latitude), math.radians(loc.longitude)
                dphi = lat2 - lat1
                dlambda = lon2 - lon1
                a = (
                    math.sin(dphi / 2) ** 2
                    + math.cos(lat1) * math.cos(lat2) * math.sin(dlambda / 2) ** 2
                )
                dist_km = 6371.0 * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                if dist_km <= max_distance_km:
                    return cl

        # 3. Fallback: match by sector without location if location is unresolved
        if not location_id and latitude is None:
            return (
                self.db.query(NeedsCluster)
                .filter(
                    NeedsCluster.issue_type == issue_type,
                    NeedsCluster.location_id.is_(None),
                    NeedsCluster.status.in_(["forming", "active"]),
                )
                .first()
            )

        return None
