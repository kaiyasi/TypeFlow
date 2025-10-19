"""add indexes for performance optimization

Revision ID: 0002
Revises: 0001
Create Date: 2025-10-17

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002'
down_revision = 'b552bd517fa7'
branch_labels = None
depends_on = None


def upgrade():
    # Users 表索引
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_users_auth_provider', 'users', ['auth_provider'])
    op.create_index('idx_users_created_at', 'users', ['created_at'])
    
    # Articles 表索引
    op.create_index('idx_articles_language_status', 'articles', ['language', 'status'])
    op.create_index('idx_articles_created_at', 'articles', ['created_at'])
    op.create_index('idx_articles_submitted_by', 'articles', ['submitted_by_id'])
    op.create_index('idx_articles_status', 'articles', ['status'])
    
    # TypingSessions 表索引
    op.create_index('idx_sessions_user_id', 'typing_sessions', ['user_id'])
    op.create_index('idx_sessions_article_id', 'typing_sessions', ['article_id'])
    op.create_index('idx_sessions_started_at', 'typing_sessions', ['started_at'])
    op.create_index('idx_sessions_mode_seconds', 'typing_sessions', ['mode_seconds'])
    
    # Scores 表索引
    op.create_index('idx_scores_session_id', 'scores', ['session_id'])
    op.create_index('idx_scores_language_wpm', 'scores', ['language', sa.text('wpm DESC')])
    op.create_index('idx_scores_created_at', 'scores', ['created_at'])
    op.create_index('idx_scores_language_created', 'scores', ['language', 'created_at'])
    
    # 複合索引用於排行榜查詢
    op.execute('''
        CREATE INDEX idx_scores_leaderboard 
        ON scores(language, created_at, wpm DESC) 
        WHERE is_void = false
    ''')


def downgrade():
    # 移除所有索引
    op.drop_index('idx_users_email', 'users')
    op.drop_index('idx_users_auth_provider', 'users')
    op.drop_index('idx_users_created_at', 'users')
    
    op.drop_index('idx_articles_language_status', 'articles')
    op.drop_index('idx_articles_created_at', 'articles')
    op.drop_index('idx_articles_submitted_by', 'articles')
    op.drop_index('idx_articles_status', 'articles')
    
    op.drop_index('idx_sessions_user_id', 'typing_sessions')
    op.drop_index('idx_sessions_article_id', 'typing_sessions')
    op.drop_index('idx_sessions_started_at', 'typing_sessions')
    op.drop_index('idx_sessions_mode_seconds', 'typing_sessions')
    
    op.drop_index('idx_scores_session_id', 'scores')
    op.drop_index('idx_scores_language_wpm', 'scores')
    op.drop_index('idx_scores_created_at', 'scores')
    op.drop_index('idx_scores_language_created', 'scores')
    op.drop_index('idx_scores_leaderboard', 'scores')

