from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.users import User
from app.models.organizations import Organization, Group, GroupMember, GroupRole
from app.models.sessions import TypingSession, Score

router = APIRouter()


class GroupInfo(BaseModel):
    id: UUID
    name: str
    organization_id: UUID
    role: str

    class Config:
        from_attributes = True


class CreatePayload(BaseModel):
    name: str


class JoinPayload(BaseModel):
    group_id: UUID


class GroupScoreItem(BaseModel):
    user_id: UUID
    display_name: str
    user_picture: Optional[str] = None
    wpm: float
    accuracy: float
    created_at: str


async def _get_user_group(db: AsyncSession, user_id: UUID) -> Optional[GroupMember]:
    res = await db.execute(select(GroupMember).where(GroupMember.user_id == user_id))
    return res.scalar_one_or_none()


@router.get("/group/me", response_model=Optional[GroupInfo])
async def get_my_group(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    gm = await _get_user_group(db, current_user.id)
    if not gm:
        return None
    # load group
    res = await db.execute(select(Group).where(Group.id == gm.group_id))
    g = res.scalar_one_or_none()
    if not g:
        return None
    return GroupInfo(id=g.id, name=g.name, organization_id=g.organization_id, role=gm.role_in_group.value)


@router.post("/group/create", response_model=GroupInfo)
async def create_group(
    payload: CreatePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # one group per user constraint
    gm = await _get_user_group(db, current_user.id)
    if gm:
        raise HTTPException(status_code=400, detail="User already in a group")

    # find or create org for the user
    org_res = await db.execute(select(Organization).where(Organization.owner_user_id == current_user.id))
    org = org_res.scalar_one_or_none()
    if not org:
        org = Organization(name=f"{current_user.display_name}'s Org", owner_user_id=current_user.id)
        db.add(org)
        await db.commit()
        await db.refresh(org)

    group = Group(organization_id=org.id, name=payload.name)
    db.add(group)
    await db.commit()
    await db.refresh(group)

    # add creator as manager
    db.add(GroupMember(group_id=group.id, user_id=current_user.id, role_in_group=GroupRole.MANAGER))
    await db.commit()

    return GroupInfo(id=group.id, name=group.name, organization_id=group.organization_id, role=GroupRole.MANAGER.value)


@router.post("/group/join", response_model=GroupInfo)
async def join_group(
    payload: JoinPayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    gm = await _get_user_group(db, current_user.id)
    if gm:
        raise HTTPException(status_code=400, detail="User already in a group")

    # must exist
    res = await db.execute(select(Group).where(Group.id == payload.group_id))
    group = res.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    db.add(GroupMember(group_id=group.id, user_id=current_user.id, role_in_group=GroupRole.MEMBER))
    await db.commit()
    return GroupInfo(id=group.id, name=group.name, organization_id=group.organization_id, role=GroupRole.MEMBER.value)


@router.get("/group/leaderboard")
async def group_leaderboard(
    mode: str = "latest",  # latest | best | average
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # any group member can view
    gm = await _get_user_group(db, current_user.id)
    if not gm:
        raise HTTPException(status_code=403, detail="Not in a group")

    # get all members of the group
    mem_res = await db.execute(select(GroupMember.user_id).where(GroupMember.group_id == gm.group_id))
    uids = [row[0] for row in mem_res.fetchall()]
    if not uids:
        return []

    mode_norm = (mode or "latest").lower()
    if mode_norm not in {"latest", "best", "average"}:
        raise HTTPException(status_code=400, detail="Invalid mode. Use one of: latest, best, average")

    items: List[GroupScoreItem] = []

    if mode_norm == "latest":
        # Latest entry per user
        query = (
            select(
                TypingSession.user_id,
                User.display_name,
                User.picture,
                Score.wpm,
                Score.accuracy,
                Score.created_at,
            )
            .join(TypingSession, Score.session_id == TypingSession.id)
            .join(User, TypingSession.user_id == User.id, isouter=True)
            .where(and_(TypingSession.user_id.in_(uids), Score.is_void == False))
            .order_by(TypingSession.user_id, desc(Score.created_at))
        )

        latest_map = {}
        res = await db.execute(query)
        for row in res.fetchall():
            uid = row[0]
            if uid not in latest_map:
                latest_map[uid] = row

        for uid, row in latest_map.items():
            items.append(
                GroupScoreItem(
                    user_id=uid,
                    display_name=row[1] or "User",
                    user_picture=row[2],
                    wpm=float(row[3]) if row[3] is not None else 0.0,
                    accuracy=float(row[4]) if row[4] is not None else 0.0,
                    created_at=str(row[5]),
                )
            )

    elif mode_norm == "best":
        # Best entry per user (highest WPM, tie-break by accuracy then recency)
        query = (
            select(
                TypingSession.user_id,
                User.display_name,
                User.picture,
                Score.wpm,
                Score.accuracy,
                Score.created_at,
            )
            .join(TypingSession, Score.session_id == TypingSession.id)
            .join(User, TypingSession.user_id == User.id, isouter=True)
            .where(and_(TypingSession.user_id.in_(uids), Score.is_void == False))
            .order_by(
                TypingSession.user_id,
                desc(Score.wpm),
                desc(Score.accuracy),
                desc(Score.created_at),
            )
        )

        best_map = {}
        res = await db.execute(query)
        for row in res.fetchall():
            uid = row[0]
            if uid not in best_map:
                best_map[uid] = row

        for uid, row in best_map.items():
            items.append(
                GroupScoreItem(
                    user_id=uid,
                    display_name=row[1] or "User",
                    user_picture=row[2],
                    wpm=float(row[3]) if row[3] is not None else 0.0,
                    accuracy=float(row[4]) if row[4] is not None else 0.0,
                    created_at=str(row[5]),
                )
            )

    else:  # average
        # Average per user across all non-void scores; created_at shows most recent score time
        query = (
            select(
                TypingSession.user_id,
                User.display_name,
                User.picture,
                func.avg(Score.wpm),
                func.avg(Score.accuracy),
                func.max(Score.created_at),
            )
            .join(TypingSession, Score.session_id == TypingSession.id)
            .join(User, TypingSession.user_id == User.id, isouter=True)
            .where(and_(TypingSession.user_id.in_(uids), Score.is_void == False))
            .group_by(TypingSession.user_id, User.display_name, User.picture)
        )

        res = await db.execute(query)
        for row in res.fetchall():
            items.append(
                GroupScoreItem(
                    user_id=row[0],
                    display_name=row[1] or "User",
                    user_picture=row[2],
                    wpm=float(row[3]) if row[3] is not None else 0.0,
                    accuracy=float(row[4]) if row[4] is not None else 0.0,
                    created_at=str(row[5]) if row[5] is not None else "",
                )
            )

    # sort for response: by WPM then accuracy desc
    items.sort(key=lambda x: (-x.wpm, -x.accuracy))
    return items


class InvitePayload(BaseModel):
    email: str


@router.post("/group/invite")
async def invite_member(
    payload: InvitePayload,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Only manager can invite
    gm = await _get_user_group(db, current_user.id)
    if not gm:
        raise HTTPException(status_code=403, detail="Not in a group")
    if gm.role_in_group != GroupRole.MANAGER:
        raise HTTPException(status_code=403, detail="Only group manager can invite")

    # Find user by email
    u_res = await db.execute(select(User).where(User.email == payload.email))
    user = u_res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure the user is not already in a group
    exists = await _get_user_group(db, user.id)
    if exists:
        raise HTTPException(status_code=400, detail="User already in a group")

    db.add(GroupMember(group_id=gm.group_id, user_id=user.id, role_in_group=GroupRole.MEMBER))
    await db.commit()
    return {"message": "Invited"}


@router.post("/group/leave")
async def leave_group(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    gm = await _get_user_group(db, current_user.id)
    if not gm:
        raise HTTPException(status_code=400, detail="Not in a group")

    # Remove membership
    # Using raw delete via select then delete from session
    await db.execute(
        GroupMember.__table__.delete().where(
            and_(GroupMember.group_id == gm.group_id, GroupMember.user_id == current_user.id)
        )
    )
    await db.commit()
    return {"message": "Left group"}
