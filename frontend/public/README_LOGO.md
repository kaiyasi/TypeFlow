# Logo placement

Place your new logo file here:

- Path: `frontend/public/logo.png`
- Recommended max size: < 512 KB
- Recommended dimensions:
  - Square: 1024 × 1024 (PNG)
  - Wide header: 512 × 128 (PNG or SVG)

Favicon (optional):
- `frontend/public/favicon.svg` (current default)
- Optionally add:
  - `frontend/public/favicon-32x32.png`
  - `frontend/public/favicon-16x16.png`
  - `frontend/public/apple-touch-icon.png`

Notes:
- Files in `public/` are served at the site root. So `/logo.png` maps to `frontend/public/logo.png`.
- The header logo is controlled by `site.config.ts` → `siteConfig.logo`.
- If you switch to SVG, set `siteConfig.logo` to `/logo.svg`.
