from snakemake_logger_plugin_sqlite.models.base import Base
from snakemake_logger_plugin_sqlite.models.enums import Status

from sqlalchemy import JSON, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, Dict, Any, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from snakemake_logger_plugin_sqlite.models.rule import Rule
    from snakemake_logger_plugin_sqlite.models.error import Error


class Workflow(Base):
    __tablename__ = "workflows"  # Using plural for consistency
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    snakefile: Mapped[Optional[str]]
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow())
    end_time: Mapped[Optional[datetime]]
    status: Mapped[Status] = mapped_column(Enum(Status), default="UNKNOWN")
    command_line: Mapped[Optional[str]]
    dryrun: Mapped[bool]
    rulegraph_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON, nullable=True
    )
    rules: Mapped[list["Rule"]] = relationship(
        "Rule",
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="selectin",  # This helps with N+1 query performance
    )
    errors: Mapped[list["Error"]] = relationship(
        "Error",
        back_populates="workflow",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
