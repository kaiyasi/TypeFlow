from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.users import User, UserRole
from app.models.organizations import Organization, Group, GroupMember, GroupRole
from app.models.sessions import TypingSession, Score

router = APIRouter()


class Classroom(BaseModel):
    id: UUID
    name: str
    organization_id: UUID

    class Config:
        from_attributes = True


class ClassroomCreate(BaseModel):
    name: str


class MemberAdd(BaseModel):
    email: str
    role: Optional[str] = "member"  # member | manager


class StudentScoreItem(BaseModel):
    user_id: UUID
    display_name: str
    email: Optional[str]
    latest_wpm: Optional[float]
    latest_accuracy: Optional[float]
    latest_at: Optional[str]
    best_wpm: Optional[float]
    avg_wpm: Optional[float]
    avg_accuracy: Optional[float]
    sessions: int


async def _ensure_teacher_org(db: AsyncSession, user: User) -> Organization:
    # Find or create an organization owned by the teacher
    result = await db.execute(
        select(Organization).where(Organization.owner_user_id == user.id)
    )
    org = result.scalar_one_or_none()
    if org:
        return org
    org = Organization(name=f"{user.display_name}'s Classroom", owner_user_id=user.id)
    db.add(org)
    await db.commit()
    await db.refresh(org)
    return org


def _is_teacher(user: User) -> bool:
    return user.role in [UserRole.ORG_ADMIN, UserRole.SUPER_ADMIN]


@router.get("/classrooms", response_model=List[Classroom])
async def list_classrooms(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not _is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Teacher access required")

    # Classrooms managed by user: either org owner or group manager
    # First, groups from user's owned orgs
    owned_orgs = select(Organization.id).where(Organization.owner_user_id == current_user.id)
    q1 = select(Group).where(Group.organization_id.in_(owned_orgs))

    # Also groups where user is manager
    gm = select(GroupMember.group_id).where(
        and_(GroupMember.user_id == current_user.id, GroupMember.role_in_group == GroupRole.MANAGER)
    )
    q2 = select(Group).where(Group.id.in_(gm))

    res1 = await db.execute(q1)
    res2 = await db.execute(q2)
    groups = list({g.id: g for g in [*res1.scalars().all(), *res2.scalars().all()]}.values())
    return groups


@router.post("/classrooms", response_model=Classroom)
async def create_classroom(
    payload: ClassroomCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not _is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Teacher access required")

    org = await _ensure_teacher_org(db, current_user)
    group = Group(organization_id=org.id, name=payload.name)
    db.add(group)
    await db.commit()
    await db.refresh(group)

    # Make creator a manager of this classroom
    gm = GroupMember(group_id=group.id, user_id=current_user.id, role_in_group=GroupRole.MANAGER)
    db.add(gm)
    await db.commit()
    return group


@router.post("/classrooms/{classroom_id}/members")
async def add_member(
    classroom_id: UUID,
    payload: MemberAdd,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not _is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Teacher access required")

    # Check classroom exists and current user manages it
    grp_res = await db.execute(select(Group).where(Group.id == classroom_id))
    group = grp_res.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Classroom not found")

    # Verify manager rights
    owns_org = await db.execute(
        select(func.count()).select_from(Organization).where(
            and_(Organization.id == group.organization_id, Organization.owner_user_id == current_user.id)
        )
    )
    is_owner = owns_org.scalar() > 0
    mgr_res = await db.execute(
        select(func.count()).select_from(GroupMember).where(
            and_(GroupMember.group_id == classroom_id,
                 GroupMember.user_id == current_user.id,
                 GroupMember.role_in_group == GroupRole.MANAGER)
        )
    )
    is_manager = mgr_res.scalar() > 0
    if not (is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not a classroom manager")

    # Find user by email
    u_res = await db.execute(select(User).where(User.email == payload.email))
    user = u_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Upsert membership
    exists_res = await db.execute(
        select(func.count()).select_from(GroupMember).where(
            and_(GroupMember.group_id == classroom_id, GroupMember.user_id == user.id)
        )
    )
    if exists_res.scalar() == 0:
        role = GroupRole.MANAGER if payload.role == 'manager' else GroupRole.MEMBER
        db.add(GroupMember(group_id=classroom_id, user_id=user.id, role_in_group=role))
        await db.commit()
    return {"message": "Member added"}


@router.get("/classrooms/{classroom_id}/scores", response_model=List[StudentScoreItem])
async def classroom_scores(
    classroom_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not _is_teacher(current_user):
        raise HTTPException(status_code=403, detail="Teacher access required")

    # Verify access similar to add_member
    grp_res = await db.execute(select(Group).where(Group.id == classroom_id))
    group = grp_res.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Classroom not found")

    owns_org = await db.execute(
        select(func.count()).select_from(Organization).where(
            and_(Organization.id == group.organization_id, Organization.owner_user_id == current_user.id)
        )
    )
    is_owner = owns_org.scalar() > 0
    mgr_res = await db.execute(
        select(func.count()).select_from(GroupMember).where(
            and_(GroupMember.group_id == classroom_id,
                 GroupMember.user_id == current_user.id,
                 GroupMember.role_in_group == GroupRole.MANAGER)
        )
    )
    is_manager = mgr_res.scalar() > 0
    if not (is_owner or is_manager):
        raise HTTPException(status_code=403, detail="Not a classroom manager")

    # Get members
    mem_res = await db.execute(
        select(GroupMember.user_id).where(GroupMember.group_id == classroom_id)
    )
    member_ids = [row[0] for row in mem_res.fetchall()]
    if not member_ids:
        return []

    # Aggregate scores per member
    # latest score per member
    latest_sub = (
        select(
            Score.session_id,
            TypingSession.user_id.label('user_id'),
            Score.wpm,
            Score.accuracy,
            Score.created_at
        )
        .join(TypingSession, Score.session_id == TypingSession.id)
        .where(
            and_(TypingSession.user_id.in_(member_ids),
                 Score.is_void == False)
        )
        .order_by(TypingSession.user_id, desc(Score.created_at))
    )

    # Best and averages per member
    agg_query = (
        select(
            TypingSession.user_id.label('user_id'),
            func.max(Score.wpm).label('best_wpm'),
            func.avg(Score.wpm).label('avg_wpm'),
            func.avg(Score.accuracy).label('avg_accuracy'),
            func.count(Score.id).label('sessions')
        )
        .join(TypingSession, Score.session_id == TypingSession.id)
        .where(
            and_(TypingSession.user_id.in_(member_ids), Score.is_void == False)
        )
        .group_by(TypingSession.user_id)
    )

    agg_res = await db.execute(agg_query)
    agg_map = {row[0]: row for row in agg_res.fetchall()}

    # For latest per user, pick top row per user from latest_sub
    latest_map = {}
    latest_res = await db.execute(latest_sub)
    for row in latest_res.fetchall():
        uid = row[1]
        if uid not in latest_map:
            latest_map[uid] = row

    # Build result with user info
    users_res = await db.execute(select(User).where(User.id.in_(member_ids)))
    users = {u.id: u for u in users_res.scalars().all()}

    results: List[StudentScoreItem] = []
    for uid in member_ids:
        u = users.get(uid)
        if not u:
            continue
        agg = agg_map.get(uid)
        latest = latest_map.get(uid)
        results.append(StudentScoreItem(
            user_id=uid,
            display_name=u.display_name,
            email=u.email,
            latest_wpm=float(latest[2]) if latest else None,
            latest_accuracy=float(latest[3]) if latest else None,
            latest_at=str(latest[4]) if latest else None,
            best_wpm=float(agg[1]) if agg else None,
            avg_wpm=float(agg[2]) if agg else None,
            avg_accuracy=float(agg[3]) if agg else None,
            sessions=int(agg[4]) if agg else 0,
        ))

    return results

