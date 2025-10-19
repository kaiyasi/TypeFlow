from sqlalchemy import Column, String, DateTime, UUID, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
import enum
from app.core.database import Base

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    owner_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    owner = relationship("User")
    
    def __repr__(self):
        return f"<Organization {self.name}>"

class Group(Base):
    __tablename__ = "groups"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization", backref="groups")
    
    def __repr__(self):
        return f"<Group {self.name}>"

class GroupRole(enum.Enum):
    MEMBER = "member"
    MANAGER = "manager"

class GroupMember(Base):
    __tablename__ = "group_members"
    
    group_id = Column(UUID(as_uuid=True), ForeignKey("groups.id"), primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), primary_key=True)
    role_in_group = Column(Enum(GroupRole), default=GroupRole.MEMBER, nullable=False)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    group = relationship("Group", backref="members")
    user = relationship("User")
    
    def __repr__(self):
        return f"<GroupMember {self.user_id} in {self.group_id}>"