from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Enum, UUID, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class ArticleStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"

class Language(enum.Enum):
    EN = "en"
    CODE = "code"
    ZH_TW = "zh-TW"
    ZH_CN = "zh-CN"
    KO = "ko"
    JA = "ja"
    DE = "de"
    RU = "ru"
    ES = "es"
    FR = "fr"
    IT = "it"
    PT = "pt"
    VI = "vi"

class Article(Base):
    __tablename__ = "articles"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False)
    language = Column(Enum(Language), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(Enum(ArticleStatus), default=ArticleStatus.DRAFT, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    
    # User relationships
    submitted_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # Review information
    review_note = Column(Text, nullable=True)
    published_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    source = Column(String(100), nullable=True)  # Source attribution
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    submitter = relationship("User", foreign_keys=[submitted_by_id])
    reviewer = relationship("User", foreign_keys=[reviewed_by_id])
    
    def __repr__(self):
        return f"<Article {self.title} ({self.language.value})>"

class ArticleRevision(Base):
    __tablename__ = "article_revisions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    article_id = Column(UUID(as_uuid=True), ForeignKey("articles.id"), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    article = relationship("Article", backref="revisions")
    creator = relationship("User")
    
    def __repr__(self):
        return f"<ArticleRevision {self.article_id} v{self.version}>"
