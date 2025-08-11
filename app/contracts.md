# API Contracts and Integration Plan

Scope: Implement backend for palettes, session-based preferences, and email capture. Replace frontend mocks progressively.

Base URL
- Frontend must use REACT_APP_BACKEND_URL and prefix all routes with /api
- Backend binds 0.0.0.0:8001 (managed by supervisor)

Collections (MongoDB)
- palettes
  - id (string, unique)
  - name, bg, color, baseBg, baseColor, accent, subtle (strings)
- preferences
  - session_id (string, unique)
  - palette_id (string, references palettes.id)
  - updated_at (datetime, UTC)
- notify_emails
  - email (string, unique, format email)
  - created_at (datetime, UTC)
  - updated_at (datetime, UTC)

Seed Data
- On startup, if palettes is empty, insert curated palettes (same as frontend mock).

Endpoints
1) GET /api/palettes
   - Response: Palette[]
   - 200 OK: [{ id, name, bg, color, baseBg, baseColor, accent, subtle }]

2) POST /api/preferences
   - Purpose: Save selected palette for an anonymous session
   - Request (JSON): { palette_id: string, session_id?: string }
   - Behavior:
     - If session_id not provided, generate a new UUID v4
     - Validate palette_id exists
     - Upsert by session_id
   - Response 200/201: { session_id: string, palette_id: string, updated_at: ISO8601 }
   - Errors:
     - 404 if palette not found: { detail: "Palette not found" }

3) POST /api/notify
   - Purpose: Capture email for notifications
   - Request (JSON): { email: string }
   - Behavior: Upsert on email, set created_at if new, updated_at otherwise
   - Response 200: { status: "ok" }
   - Errors: 422 validation for invalid email

Frontend Integration Plan
- Create src/lib/api.js with axios wrappers using process.env.REACT_APP_BACKEND_URL
- Home.jsx
  - Fetch palettes on mount via getPalettes(); fall back to mock if fail
  - Maintain session id in localStorage (key: tp_session_id)
  - On theme apply: POST /api/preferences with palette_id and session id
  - Inline email capture: POST /api/notify and show toast
- ThemePicker.jsx
  - Accept palettesData prop to render server palettes when available
  - Keep existing local preview & localStorage theme variables

Mock Replacement
- Mock palettes in src/mock.js remain as fallback only
- After backend is stable, we may remove direct import of palettes in future refactor

Testing
- Backend: run deep_testing_backend_v2 on the 3 endpoints, verify seeding, upsert behavior, and error handling
- Frontend: manual + optional automated tests for fetching palettes, saving preference (session persist), and email capture toast