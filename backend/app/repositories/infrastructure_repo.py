"""Repository for reference data: InfrastructureAsset, DemographicIndicator, Project, PublicDataset."""

from __future__ import annotations

from typing import Optional

from sqlalchemy.orm import Session

from app.models import DemographicIndicator, InfrastructureAsset, Location, Project, PublicDataset


class InfrastructureRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def list_assets(
        self, asset_type: Optional[str] = None, district: Optional[str] = None
    ) -> list[InfrastructureAsset]:
        query = self.db.query(InfrastructureAsset)
        if asset_type:
            query = query.filter(InfrastructureAsset.asset_type == asset_type)
        if district:
            query = query.join(Location, InfrastructureAsset.location_id == Location.id, isouter=True).filter(
                Location.district.ilike(f"%{district}%")
            )
        return query.all()

    def list_demographics(self, district: Optional[str] = None) -> list[DemographicIndicator]:
        query = self.db.query(DemographicIndicator)
        if district:
            query = query.join(Location, DemographicIndicator.location_id == Location.id, isouter=True).filter(
                Location.district.ilike(f"%{district}%")
            )
        return query.all()

    def find_conflicting_project(
        self, sector: str, location_id: Optional[int] = None
    ) -> Optional[Project]:
        """Check whether a related ongoing or sanctioned project exists (FR-042)."""
        query = self.db.query(Project).filter(
            Project.sector.ilike(f"%{sector}%"),
            Project.status.in_(["sanctioned", "ongoing"]),
        )
        if location_id is not None:
            query = query.filter(Project.location_id == location_id)
        return query.first()

    def list_projects(
        self, sector: Optional[str] = None, status: Optional[str] = None
    ) -> list[Project]:
        query = self.db.query(Project)
        if sector:
            query = query.filter(Project.sector == sector)
        if status:
            query = query.filter(Project.status == status)
        return query.all()

    def list_datasets(self) -> list[PublicDataset]:
        return self.db.query(PublicDataset).all()
