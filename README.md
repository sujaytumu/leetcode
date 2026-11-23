# LeetCode Practice Platform

A LeetCode-style practice app.

- **Backend:** Java 21, Spring Boot 3, Spring Data JPA (H2 for dev, PostgreSQL for prod)
- **Code execution:** sandboxed through [Judge0](https://github.com/judge0/judge0) (optional, configured via `JUDGE0_URL`)
- **Frontend:** Next.js + TypeScript with the Monaco editor

## Quick start with Docker

```bash
docker compose up --build
```

Frontend: http://localhost:3000, backend: http://localhost:8080. The backend uses in-memory H2 unless you set the
Neon variables (see below) in a root-level `.env`. The frontend calls the backend from the browser, so
`NEXT_PUBLIC_API_URL` must be a URL your browser can reach; it is baked in at build time.

## Frontend

```bash
cd frontend
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8080
npm ci
npm run dev
```

CI (`.github/workflows/ci.yml`) runs `mvn verify` for the backend and `npm test` plus `npm run build` (which type-checks) for the frontend.
Frontend unit tests use Node's built-in runner (`cd frontend && npm test`, Node 22.6+), with no extra dependencies.

## Deploying (Render + Vercel + Neon)

1. **Neon:** create a project and note the JDBC URL, user and password (see "Using Neon Postgres" below).
2. **Render (backend):** Dashboard -> New -> Blueprint -> select this repo. `render.yaml` defines the service. Enter
   `DB_URL`, `DB_USER`, `DB_PASSWORD`, and leave `CORS_ALLOWED_ORIGINS` blank for now. Wait for the deploy and copy the
   URL, e.g. `https://leetcode-backend-xxxx.onrender.com`. Check `<url>/actuator/health` returns `UP`.
3. **Vercel (frontend):** Add New -> Project -> import this repo, set **Root Directory** to `frontend`, and add the
   environment variable `NEXT_PUBLIC_API_URL` = your Render URL. Deploy and copy the Vercel URL.
4. Back in Render, set `CORS_ALLOWED_ORIGINS` to the Vercel URL (no trailing slash) and redeploy.

Notes: Render's free plan sleeps after inactivity, so the first request can take about a minute. Run and Submit
need a Judge0 instance (`JUDGE0_URL`); without one the app browses problems and tracks bookmarks but cannot execute code.

## Backend

```bash
cd backend
mvn spring-boot:run
```

The API runs on http://localhost:8080 and Swagger UI is at `/swagger-ui.html`. By default it uses an in-memory H2
database, so it works with zero setup.

### Using Neon Postgres

1. Create a project at [neon.tech](https://neon.tech) and copy the connection details.
2. `cp backend/.env.example backend/.env` and fill in `DB_URL`, `DB_USER` and `DB_PASSWORD`
   (Neon shows `postgresql://user:pass@host/db?sslmode=require`; for JDBC use
   `jdbc:postgresql://host/db?sslmode=require` and put the user and password in their own variables).
3. Keep `spring.profiles.active=prod` in that file (in Docker or on a host, set the `SPRING_PROFILES_ACTIVE=prod`
   environment variable instead), then run `mvn spring-boot:run` as usual.

Tables are created on first start and the 205 seed problems are inserted. If you use Neon's pooled host (`-pooler`),
append `&prepareThreshold=0` to the URL. Never commit `.env`; it is git-ignored.

| Endpoint | Purpose |
| --- | --- |
| `GET /api/problems` | Search and filter (`q`, `difficulty`, `tag`, `status`, `bookmarked`, `page`, `size`) |
| `GET /api/problems/{slug}` | Problem detail, starter code and sample cases |
| `GET /api/tags` | All topic tags |
| `GET /api/problems/{slug}/study` | Hints, approach and complexity (204 if a problem has no write-up) |
| `GET /api/plans` | Curated study plans with their problems and your progress |
| `GET /api/daily?date=YYYY-MM-DD` | Daily challenge for a day (same problem for everyone) |
| `POST /api/problems/{slug}/run` | Run code against sample cases |
| `POST /api/problems/{slug}/submit` | Judge against all cases and record the submission |
| `GET /api/problems/{slug}/submissions` | Submission history |
| `PUT` / `DELETE /api/problems/{slug}/bookmark` | Bookmark toggle |
| `GET /api/progress` | Solved / attempted counts |
| `GET` / `POST /api/problems/{slug}/comments` | Discussion thread (`sort=top\|new`); post a comment or a reply (`parentId`) |
| `PUT` / `DELETE /api/comments/{id}/vote` | Upvote a comment; `DELETE /api/comments/{id}` removes your own |
| `GET /api/leaderboard?limit=` | Global ranking by points (Easy 10, Medium 20, Hard 40) plus your own rank |
| `POST /api/playground/run` | Run any program once with custom stdin, nothing stored |
| `GET /api/contests`, `GET /api/contests/{id}` | Weekly contest schedule, problems (after start) and live standings |
| `GET /api/submissions?verdict=&page=` | Your submissions across all problems |
| `POST /api/auth/register` | Create an account with `{email, password}` (optional `username`, derived from the email when omitted); adopts this browser's `X-Client-Id`, so existing progress is kept |
| `POST /api/auth/login` | Log in with `{email, password}` (older accounts can still send `{username, password}`); returns `{token, clientId, username, email}` (rate limited per identifier and IP) |
| `GET /api/auth/me`, `POST /api/auth/password` | Current account (`username`, `email`); change password (revokes older tokens, returns a fresh session) |

Per-user state is keyed by a UUID sent in the `X-Client-Id` header. Anonymous visitors get one automatically. An account
owns one such id: after `register`, requests must carry `Authorization: Bearer <token>` (the backend then overrides
`X-Client-Id` with the account's id, so it cannot be forged), and using that id without a token returns 401.
Passwords are hashed with PBKDF2-HMAC-SHA256 (210k iterations, per-password salt); tokens are HMAC-signed and expire
after 30 days. Set `AUTH_SECRET` (32+ random characters) in production so tokens survive restarts.

**Email (Resend).** Set `RESEND_API_KEY`, `MAIL_FROM` (a sender on a domain verified in Resend; Resend's default test
sender only delivers to your own Resend account address) and `FRONTEND_URL` (used for links in emails). That enables:
`POST /api/auth/forgot` + `POST /api/auth/reset` (a single-use link valid for 30 minutes; only a hash of the token is
stored, every request answers the same whether or not the email exists, and a reset signs out all other sessions), and
an opt-in daily problem email (`GET/PUT /api/auth/email-prefs`, one-click `POST /api/auth/unsubscribe` from the link in
each email). The daily email goes out once a day after `DAILY_EMAIL_HOUR` (default 8) in `DAILY_EMAIL_ZONE` (default
`Asia/Kolkata`); it checks every 15 minutes, so a sleeping free-tier server still catches up when it wakes. Resend's
free plan allows about 100 emails per day. Without `RESEND_API_KEY` nothing is sent.

## Features

Problem list with sorting, filters, study-path numbering and acceptance rates; a LeetCode-style workspace (resizable
panes, Monaco editor, custom testcases, run/submit with runtime and memory percentiles, editorial, answers, notes,
timer); Discuss tab with Markdown comments, replies and upvotes; topics, study plans and your own lists; mock
interviews; weekly contests (Sundays 02:30 UTC, 90 minutes, 3/4/5/6 points, 5 minute penalties); leaderboard;
playground; profile with heatmap, streaks, badges, global rank and a device sync code; command palette (Ctrl/⌘+K);
light and dark themes; offline-first catalogue and PWA manifest.

Also: email + password accounts with an account settings page (change password, log out); a daily goal ring on the profile; a
`/stats` page (verdicts, languages, weekday and hour charts, first-try rate, problems that took the most attempts); line diff between
any two submissions of a problem; a spaced-repetition review queue (`/review`, intervals 1/3/7/14/30/60 days) and custom practice sessions
(`/practice`); solve times and personal bests from the workspace timer; a "continue where you left off" banner; a device backup of
local-only data; skip link, focus ring and per-page tab titles.

## Status

Work in progress.

- Backend API, 205 seeded problems (2023 test cases) and backend tests are in place.
- Frontend, Docker setup and CI are in place.

### Seed data

`backend/src/main/resources/seed/problems.json` is generated by `backend/tools/generate_seed.py`. Expected outputs
come from reference solutions in that script, and starter code is generated for Java, Python, JavaScript and C++.
Regenerate with `python3 backend/tools/generate_seed.py`. The seeder only inserts problems whose slug does not
exist yet, so it never overwrites edits.

### Tests

```bash
cd backend
mvn verify
```

Tests use a fake code executor, so no Judge0 instance is needed.

The frontend holds no problem content: problems, tags, hints, study plans and the daily challenge are all fetched from the API
(hints and plans live in `backend/src/main/resources/seed/study.json` and `plans.json`). The last server response is cached in
localStorage purely so pages paint instantly while the free-tier backend wakes up.
