"""SQLAlchemy Organization Model for Multi-Tenant SaaS Boundary."""

import uuid
from typing import List, Optional
from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base
from app.models.base import TimestampMixin


class Organization(TimestampMixin, Base):
    """
    Organization entity acting as the primary multi-tenant security and ownership boundary.
    All datasets, members, and intelligence artifacts belong to an Organization.
    """

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    logo_url: Mapped[Optional[str]] = mapped_column(
        String(1024),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        nullable=False,
    )

    # Relationships
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
    )
    datasets: Mapped[List["Dataset"]] = relationship(
        "Dataset",
        back_populates="organization",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Organization id={self.id} name='{self.name}' slug='{self.slug}'>"
