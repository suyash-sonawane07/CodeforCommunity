"""`locations` — resolved geography with PostGIS geometry (PRD §9.1, FR-027/028).

Admin hierarchy is intentionally generic (BRICS-extensible, PRD §20):
state → district → block → village_ward.
Unresolved locations are rows with low/NULL confidence — never fabricated (FR-021/033).
"""

from typing import Optional

from geoalchemy2 import Geometry
from sqlalchemy import Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.models._mixins import TimestampMixin


class Location(Base, TimestampMixin):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    block: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    village_ward: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)  # FR-028
    resolution_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="resolved")  # | location_unresolved
    uncertainty_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
