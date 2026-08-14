"""SQLAlchemy OrganizationMember Model for Tenant Memberships and Roles."""

import uuid
from sqlalchemy import Enum as SQLEnum, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.constants import OrgRole
from app.database.base import Base
from app.models.base import TimestampMixin


class OrganizationMember(TimestampMixin, Base):
    """
    Join entity binding a User to an Organization with an assigned tenant-scoped OrgRole.
    """

    __tablename__ = "organization_members"
    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_org_member_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )
    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[OrgRole] = mapped_column(
        SQLEnum(OrgRole, name="org_role"),
        default=OrgRole.ANALYST,
        index=True,
        nullable=False,
    )

    # Relationships
    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )
    user: Mapped["User"] = relationship(
        "User",
    )

    def __repr__(self) -> str:
        return f"<OrganizationMember id={self.id} org_id={self.organization_id} user_id={self.user_id} role={self.role}>"
