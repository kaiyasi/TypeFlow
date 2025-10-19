from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum, UUID, ForeignKey, Integer
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class PositionType(enum.Enum):
    OFFSET = "offset"
    LINE = "line"

class ErrataStatus(enum.Enum):
    OPEN = "open"
    APPLIED = "applied"
    REJECTED = "rejected"

class ErrataReport(Base):
    __tablename__ = "errata_reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    reporter_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # Position information
    position_type = Column(Enum(PositionType), nullable=False)
    position_value = Column(Integer, nullable=False)
    
    # Error details
    before = Column(Text, nullable=False)  # Original text
    after = Column(Text, nullable=False)   # Corrected text
    note = Column(Text, nullable=True)     # Reporter's explanation
    
    # Status tracking
    status = Column(Enum(ErrataStatus), default=ErrataStatus.OPEN, nullable=False)
    applied_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    applied_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("Article", backref="errata_reports")
    reporter = relationship("User", foreign_keys=[reporter_id])
    applier = relationship("User", foreign_keys=[applied_by])
    
    def __repr__(self):
        return f"<ErrataReport {self.id} for article {self.article_id}>"

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_agent_hash = Column(String(64), unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Device {self.user_agent_hash[:8]}...>"