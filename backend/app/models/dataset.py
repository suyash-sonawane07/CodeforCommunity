"""Reference-data entities: `public_datasets`, `infrastructure_assets`,
`demographic_indicators`, `projects` (PRD §9.1, §6.5).

Every row carries `dataset_version` + provenance label (FR-038/057):
source_label ∈ {confirmed, candidate, synthetic}.
"""

from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import TimestampMixin


class PublicDataset(Base, TimestampMixin):
    __tablename__ = "public_datasets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(150), unique=True)
    source_label: Mapped[str] = mapped_column(String(20))  # confirmed|candidate|synthetic
    version: Mapped[str] = mapped_column(String(50))
    ingested_at: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class InfrastructureAsset(Base, TimestampMixin):
    __tablename__ = "infrastructure_assets"

    id: Mapped[int] = mapped_column(primary_key=True)
    asset_type: Mapped[str] = mapped_column(String(50), index=True)  # school|clinic|bus_stop|...
    name: Mapped[str] = mapped_column(String(200))
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    dataset_version: Mapped[str] = mapped_column(String(50))  # FR-038
    attributes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON attributes


class DemographicIndicator(Base, TimestampMixin):
    __tablename__ = "demographic_indicators"

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    population: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)  # FR-031
    deprivation_index: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # equity proxy
    dataset_version: Mapped[str] = mapped_column(String(50))  # FR-038
    indicator_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)


class Project(Base, TimestampMixin):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    sector: Mapped[str] = mapped_column(String(50), index=True)
    status: Mapped[str] = mapped_column(String(30))  # sanctioned|ongoing|completed
    location_id: Mapped[Optional[int]] = mapped_column(ForeignKey("locations.id"), nullable=True)
    dataset_version: Mapped[str] = mapped_column(String(50))  # FR-038
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
