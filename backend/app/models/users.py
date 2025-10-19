from sqlalchemy import Column, String, DateTime, Boolean, Text, Enum, UUID
from sqlalchemy.sql import func
import uuid
import enum
from app.core.database import Base

class AuthProvider(enum.Enum):
    GOOGLE = "google"
    GUEST = "guest"

class UserRole(enum.Enum):
    USER = "user"
    ORG_ADMIN = "org_admin"
    SUPER_ADMIN = "super_admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    display_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=True)  # Nullable for guests
    auth_provider = Column(Enum(AuthProvider), nullable=False)
    guest_device_hash = Column(String(64), nullable=True)  # For guest users
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Reserved for future use
    picture = Column(String(512), nullable=True)  # Google profile picture URL
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_locked = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<User {self.display_name} ({self.email or self.guest_device_hash})>"