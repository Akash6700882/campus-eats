# Campus Eats

A production-oriented campus food delivery platform for a single college canteen — customer ordering, kitchen workflow, delivery dispatch, and admin analytics, with campus-geofenced delivery and Razorpay payments.

> **Status:** Under active build, phase by phase. See `docs/PROGRESS.md` for what's implemented so far.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, Redis, Celery, WebSockets
- **Frontend:** React + TypeScript + Vite, Tailwind CSS, React Query, React Hook Form + Zod
- **Payments:** Razorpay (test mode)
- **Maps:** Google Maps JavaScript API
- **Images:** Cloudinary

## Local development

1. Copy env files and fill in test-mode credentials:
   ```
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```
2. Start the stack:
   ```
   docker-compose up --build
   ```
3. Services:
   - Backend API: http://localhost:8000 (Swagger UI at `/docs`)
   - Frontend: http://localhost:5173
   - Combined via nginx: http://localhost:8080
4. Health check: `curl http://localhost:8000/health`

## Roles & default admin

Four roles: `customer`, `admin`, `kitchen`, `delivery`. A default admin account is seeded from `DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD` in `backend/.env` (see Phase 1 seed script once added).

## Required third-party accounts (test/sandbox mode is enough)

| Service | Used for | Get keys from |
|---|---|---|
| Razorpay | Payments | https://dashboard.razorpay.com/app/keys (Test Mode) |
| Google Maps | Location picker, campus geofence, delivery navigation | https://console.cloud.google.com/google/maps-apis |
| Cloudinary | Food/review image uploads | https://cloudinary.com/console |
| SMTP | Email notifications | Any SMTP provider (e.g. Gmail app password) |

SMS/WhatsApp default to a console-log stub in development (`SMS_PROVIDER=console`) — no telephony account required until you're ready to wire in Twilio/MSG91/WhatsApp Business API.

## Project layout

See `docs/ARCHITECTURE.md` (added alongside the backend foundation in Phase 1) for the full repository layout and design decisions.
