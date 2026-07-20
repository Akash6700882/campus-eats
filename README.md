# Campus Eats

A production-oriented campus food delivery platform for a single college canteen — customer ordering, kitchen workflow, delivery dispatch, and admin analytics, with campus-geofenced delivery and Razorpay payments.

> **Status:** Under active build, phase by phase. See `docs/PROGRESS.md` for what's implemented so far.

## Stack

- **Backend:** FastAPI, SQLAlchemy 2.0 (async), Alembic, PostgreSQL, Redis, Celery, WebSockets
- **Frontend:** React + TypeScript + Vite, Tailwind CSS v4, shadcn/ui, React Query, React Hook Form + Zod, Recharts
- **Payments:** Razorpay (test mode)
- **Maps:** Google Maps JavaScript API (optional — checkout falls back to the browser Geolocation API without it)
- **Images:** Cloudinary
- **Testing:** pytest (backend), Vitest + Testing Library (frontend)
- **CI:** GitHub Actions (`.github/workflows/ci.yml`) — backend tests + lint, frontend typecheck + lint + tests + build

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
5. Seed sample data (roles, default admin, categories/foods, campus geofence):
   ```
   docker-compose exec backend python -m scripts.seed
   ```

## Roles & accounts

Four roles: `customer`, `admin`, `kitchen`, `delivery`.

- **Customer** accounts self-signup at `/signup`.
- The **default admin** is seeded from `DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD` in `backend/.env`.
- **Kitchen** and **delivery** staff accounts have no self-signup (by design) — create them directly against the database, then have an admin create a matching `DeliveryPartner` profile for delivery staff via `POST /admin/delivery-partners` (the admin dashboard's "Delivery partners" tab does this from the UI, looking up eligible users via `GET /admin/users?role=delivery`).

All four roles log in from the same `/login` page; the app redirects to the right dashboard (`/kitchen`, `/delivery`, `/admin`, or the customer home) based on the account's role.

## API docs & Postman

- Interactive Swagger UI: `http://localhost:8000/docs` (or `/redoc`)
- A ready-to-import Postman collection is checked in at [`docs/postman_collection.json`](docs/postman_collection.json), organized by resource (auth, menu, cart, orders, kitchen, delivery, admin, analytics, reviews, wishlist, notifications, ...). Import it, set the collection variables `base_url` (defaults to `http://localhost:8000/api/v1`) and `access_token` (paste the token from an `auth/login` or `auth/signup` response) — every request already uses collection-level bearer auth against `{{access_token}}`.

## Required third-party accounts (test/sandbox mode is enough)

| Service | Used for | Get keys from |
|---|---|---|
| Razorpay | Payments | https://dashboard.razorpay.com/app/keys (Test Mode) |
| Google Maps | Location picker, campus geofence, delivery navigation | https://console.cloud.google.com/google/maps-apis |
| Cloudinary | Food/review image uploads | https://cloudinary.com/console |
| SMTP | Email notifications | Any SMTP provider (e.g. Gmail app password) |

SMS/WhatsApp default to a console-log stub in development (`SMS_PROVIDER=console`) — no telephony account required until you're ready to wire in Twilio/MSG91/WhatsApp Business API. Razorpay works the same way in reverse: without real test-mode keys, payment initiation fails with a clean error instead of a broken checkout.

## Project layout

See `docs/ARCHITECTURE.md` for the full repository layout and design decisions, and `docs/PROGRESS.md` for what's implemented so far, phase by phase.
