import asyncio
from typing import List
import sys

from sqlalchemy import select

from app.core.database import get_session_maker
from app.models.users import User, UserRole, AuthProvider


async def promote_admins(emails: List[str]) -> None:
    emails = [e.strip() for e in emails if e and e.strip()]
    if not emails:
        print("No emails provided.")
        return

    SessionLocal = get_session_maker()
    async with SessionLocal() as session:
        changed = False
        for email in emails:
            result = await session.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if not user:
                display = email.split("@")[0]
                user = User(
                    display_name=display,
                    email=email,
                    auth_provider=AuthProvider.GOOGLE,
                    role=UserRole.SUPER_ADMIN,
                )
                session.add(user)
                changed = True
                print(f"Created and promoted: {email}")
            else:
                if user.role != UserRole.SUPER_ADMIN:
                    user.role = UserRole.SUPER_ADMIN
                    changed = True
                    print(f"Promoted existing user to SUPER_ADMIN: {email}")
                else:
                    print(f"Already SUPER_ADMIN: {email}")

        if changed:
            await session.commit()
        else:
            print("No changes needed.")


if __name__ == "__main__":
    # Usage: python scripts/promote_admin.py user1@example.com [user2@example.com ...]
    emails = sys.argv[1:]
    asyncio.run(promote_admins(emails))

