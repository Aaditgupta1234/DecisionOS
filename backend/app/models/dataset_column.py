"""SQLAlchemy DatasetColumn Model."""

import uuid
from typing import Optional
from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.base import Base
from app.models.base import TimestampMixin


class DatasetColumn(TimestampMixin, Base):
    """Dataset column metadata entity storing schema mapping, data types, and confidence scores."""

    __tablename__ = "dataset_columns"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    original_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    normalized_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    mapped_field: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
    )
    mapping_confidence: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
    )
    data_type: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
    )
    sample_value: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )

    # Relationships
    dataset: Mapped["Dataset"] = relationship(
        "Dataset",
        back_populates="columns",
    )

    def __repr__(self) -> str:
        return f"<DatasetColumn id={self.id} original={self.original_name} mapped={self.mapped_field} conf={self.mapping_confidence}>"
