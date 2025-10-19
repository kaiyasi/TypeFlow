"""expand language enum with more values

Revision ID: 0004
Revises: 0003
Create Date: 2025-10-19 00:20:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing enum type
    old_enum = postgresql.ENUM('EN', 'CODE', 'ZH_TW', 'ZH_CN', 'KO', 'JA', 'DE', 'RU', name='language')
    old_enum.create(op.get_bind(), checkfirst=True)

    # New enum with additional values
    new_enum = postgresql.ENUM(
        'EN', 'CODE', 'ZH_TW', 'ZH_CN', 'KO', 'JA', 'DE', 'RU',
        'ES', 'FR', 'IT', 'PT', 'VI',
        name='language_new'
    )
    new_enum.create(op.get_bind(), checkfirst=False)

    # Alter column to new enum
    op.execute("ALTER TABLE articles ALTER COLUMN language TYPE language_new USING language::text::language_new")

    # Drop old enum and rename new to original name
    op.execute('DROP TYPE language')
    op.execute('ALTER TYPE language_new RENAME TO language')


def downgrade() -> None:
    # Create old enum type
    old_enum = postgresql.ENUM('EN', 'CODE', 'ZH_TW', 'ZH_CN', 'KO', 'JA', 'DE', 'RU', name='language_old')
    old_enum.create(op.get_bind(), checkfirst=False)

    # Cast back to old enum (may fail if rows use new values)
    op.execute("ALTER TABLE articles ALTER COLUMN language TYPE language_old USING language::text::language_old")

    # Drop current enum and rename old back to language
    op.execute('DROP TYPE language')
    op.execute('ALTER TYPE language_old RENAME TO language')
