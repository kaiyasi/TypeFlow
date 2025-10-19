# TypeFlow Release Notes

## v1.0.0

Highlights
- New Morandi design theme applied to entire app
- Admin review modal overflow and meta separators fixed
- Admin: Article edit modal (title/language/status/content) + backend PUT API with revisions
- Submission: Expanded language support (en, zh-TW, zh-CN, ja, ko, de, ru, es, fr, it, pt, vi, code)
- Leaderboard: Real data from scores with HTTPS-safe client and no placeholders
- Home: Typing showcase animation, redesigned feature cards (3-wide), quick actions
- Practice: Pure-text duration underline animation, redesigned quick stats, results dialog actions
- Sessions: Submit score to backend on finish
- Classrooms (teacher): Create/list/add member by email, view per-student aggregates
- Group: One group per user, leaderboard visible to all members, invite by email, leave, copy group ID

Breaking changes
- Leaderboard API path is now `/api/leaderboard/` (trailing slash) and returns `{ entries, total_count }`
- Frontend API client enforces same-origin HTTPS baseURL to avoid mixed-content

Upgrade notes
- Rebuild docker images and restart stack: `docker compose up -d --build`
- Ensure DB migrations are applied automatically (alembic runs at startup)

Known issues
- Some pages may require cache-busting; HTML is served with no-store headers on Nginx, but CDN may cache
- Group invite expects the invited user to already have an account

