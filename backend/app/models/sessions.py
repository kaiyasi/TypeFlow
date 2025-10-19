from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum, UUID, ForeignKey, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class TypingSession(Base):
    __tablename__ = "typing_sessions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)  # Nullable for guests
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    article_version = Column(Integer, nullable=False)
    mode_seconds = Column(Integer, nullable=False)  # 60, 180, 300, 600
    
    # Session timing
    started_at = Column(DateTime(timezone=True), nullable=False)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Raw data
    raw_keystrokes_json = Column(JSON, nullable=True)  # Detailed keystroke data
    focus_blur_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User")
    article = relationship("Article")
    
    def __repr__(self):
        return f"<TypingSession {self.id} - {self.mode_seconds}s>"

class Score(Base):
    __tablename__ = "scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("typing_sessions.id"), nullable=False)
    
    # Performance metrics
    wpm = Column(Float, nullable=False)  # Net WPM
    accuracy = Column(Float, nullable=False)  # Percentage
    gross_wpm = Column(Float, nullable=False)  # Raw typing speed
    net_wpm = Column(Float, nullable=False)  # Adjusted for errors
    correct_keystrokes = Column(Integer, nullable=False)
    error_keystrokes = Column(Integer, nullable=False)
    
    # Metadata
    language = Column(String(10), nullable=False)  # Language code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Admin fields
    is_void = Column(Boolean, default=False, nullable=False)  # Voided by admin
    note = Column(Text, nullable=True)  # Admin note
    
    # Relationships
    session = relationship("TypingSession", backref="score")
    
    def __repr__(self):
        return f"<Score {self.wpm} WPM, {self.accuracy}% accuracy>"

class LeaderboardEntry(Base):
    __tablename__ = "leaderboards"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    scope = Column(Enum(enum.Enum('Scope', 'daily weekly monthly alltime')), nullable=False)
    category = Column(String(20), nullable=False)  # overall, en, code, zh-TW, etc.
    rank_json = Column(JSON, nullable=False)  # Serialized ranking data
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LeaderboardEntry {self.scope.value} {self.category}>"