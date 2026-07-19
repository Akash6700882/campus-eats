# Architecture

## Layout

```
backend/app/
├── api/v1/          # FastAPI routers: auth, menu, addresses, cart, orders, coupons,
│                    #   payments, kitchen, delivery, admin_orders, ws
├── core/            # config, db session, security (password hashing), DI helpers
├── models/          # SQLAlchemy 2.0 models — source of truth for schema, migrated via Alembic
├── schemas/         # Pydantic request/response schemas (added alongside each router)
├── repositories/     # Data-access layer: one class per model, extends BaseRepository
├── services/         # Business logic layer (coupon rules, geofence checks, pricing,
│                      #   order state machine, delivery-partner assignment...)
├── ws/               # In-memory WebSocket connection manager + order-event broadcasting
└── tasks/            # Celery app + tasks (notification dispatch, analytics rollups — not yet used)
```

Request flow: router → service (business rules) → repository (queries) → model. Routers never touch the session directly for anything beyond simple reads; repositories never contain business rules.

## Database schema (Phase 1)

17 tables, migrated with Alembic (`backend/alembic/versions/`):

- **roles**, **users** — 4 roles (customer/admin/kitchen/delivery) via FK, not a hardcoded enum column, so role metadata can grow later.
- **categories**, **foods** — menu catalog. `Food.discounted_price` is a computed property (price × (1 − discount%)), not stored, so it can never drift from `price`/`discount_percent`.
- **addresses** — campus-specific fields (building/hostel/block/room/department) + lat/lng for the geofence check.
- **delivery_zones** — campus boundary as GeoJSON Polygon text; a placeholder polygon is seeded (see below) until real GPS survey data is available.
- **cart_items** — server-persisted per-user cart (unique on user+food).
- **coupons** — percent/flat discount, min order amount, usage limits, festival/referral/general type.
- **orders**, **order_items** — order header carries the full pricing breakdown (item_total, discount, delivery/packing charge, GST, grand_total) and the `OrderStatus` state machine; `order_items` snapshot food name/price at order time so later menu edits don't rewrite history.
- **payments** — one row per payment attempt against an order (supports retry), stores Razorpay order/payment/signature IDs.
- **delivery_partners** — profile + live lat/lng + today's earnings, linked 1:1 to a `users` row with the `delivery` role.
- **reviews**, **review_likes**, **wishlist_items**, **notifications**, **inventory_items** — supporting features per the plan.

## Seed data (`backend/scripts/seed.py`)

Idempotent — safe to re-run. Creates:
- The 4 roles.
- A default admin user from `DEFAULT_ADMIN_EMAIL` / `DEFAULT_ADMIN_PASSWORD` (backend/.env).
- 7 categories and 21 sample foods covering the requested menu (idli/dosa varieties, meals, juices, etc.).
- One placeholder campus `DeliveryZone` polygon — **replace this with the real campus boundary** via the admin delivery-zone editor once available (see Phase 7 in the build plan); until then, the geofence check in Phase 4 will validate against this placeholder square.

## Order lifecycle & staff roles

`OrderStatus` (`app/models/enums.py`) and the allowed transitions between
them live in `app/services/order_state_machine.py`, enforced centrally by
`OrderService._transition`/`assert_transition_allowed` rather than scattered
across routers:

```
pending → accepted → preparing → ready → assigned → picked_up → on_the_way → delivered → refunded
   ↓          ↓           ↓
cancelled  cancelled  cancelled
```

Admin force-cancel is the one path that bypasses this table deliberately —
it can cancel from any non-terminal status, freeing the assigned delivery
partner if there was one.

Kitchen (`/kitchen/*`) and delivery (`/delivery/*`) routers only ever mutate
orders through `OrderService`, never touch the session directly. Marking an
order `ready` auto-assigns the nearest available `DeliveryPartner`
(`app/services/delivery_assignment.py`, haversine distance to the delivery
address) and generates the 6-digit `delivery_otp` the customer reads out to
the delivery partner on handoff — staff-facing `OrderResponse`s always pass
`reveal_otp=False` so the OTP never leaks to kitchen/delivery views.

## Live updates (WebSockets)

`app/ws/manager.py` is a single-process, in-memory pub/sub keyed by channel
name (`order:{id}`, `kitchen`, `delivery:{partner_id}`). Routers call
`app/ws/events.broadcast_order_event()` after each successful commit; it fans
the same payload out to the relevant channels. `/ws/orders/{id}`,
`/ws/kitchen`, `/ws/delivery` (`app/api/v1/ws.py`) authenticate via a
`?token=` query param (a browser WebSocket handshake can't carry a custom
Authorization header) and briefly borrow a DB session — acquired and released
via `get_db()` manually rather than as a request-scoped `Depends` — just to
resolve identity/ownership before entering the long-lived receive loop.

This is intentionally single-process: fine for one uvicorn worker, but a
multi-replica deployment would need to swap the in-memory channels for
Redis pub/sub (Redis is already a dependency for OTP/rate-limiting).

## Password hashing

`app/core/security.py` calls `bcrypt` directly rather than through `passlib.CryptContext` — recent `bcrypt` releases (≥4.1) dropped the `__about__` attribute passlib's backend probing depends on, which breaks `CryptContext(schemes=["bcrypt"])` at hash time. Calling `bcrypt.hashpw`/`checkpw` directly sidesteps that entirely.

## Frontend (`frontend/src/`)

```
api/         # Thin axios wrappers, one file per backend resource (auth, menu, cart, orders...)
components/
  ui/        # shadcn/ui primitives — generated, owned/patched in-place (see note below)
  layout/    # Navbar, Footer, AppLayout
  food/      # FoodCard, FoodRow, CategoryChips, VegBadge
  address/   # AddressForm (shared by checkout and profile)
  order/     # StatusTimeline
hooks/       # React Query hooks per resource (useCart, useMenu, useOrders, useAddresses...)
lib/         # api.ts (axios instance + refresh interceptor), queryClient, format, razorpay, utils
pages/customer/  # One component per route
store/       # AuthProvider, ThemeProvider (React Context, not Redux/Zustand — small enough)
types/       # Hand-written TS types mirroring the backend Pydantic schemas
```

Data flow: page → React Query hook → `api/*.ts` → axios instance (`lib/api.ts`)
with a request interceptor attaching the bearer token and a response
interceptor that transparently refreshes on 401 (single-flight, so
concurrent requests don't each trigger their own refresh) and redirects to
`/login` if the refresh token is also dead. Cart/address/order mutations
invalidate their React Query key on success rather than manually patching
the cache — simpler and correct at this app's request volume.

**Tailwind v4, not v3.** The scaffold shipped pinned to Tailwind v3, but the
current `shadcn` CLI's registry (`radix-nova` style) generates components
using v4-only syntax (`@theme`, `@custom-variant`, bracket-less `data-*`/
`has-*`/`in-*` variants). Rather than hand-patch every generated component
back to v3 conventions, the project was upgraded to Tailwind v4 +
`@tailwindcss/vite` (see `vite.config.ts`, `src/index.css`); `tailwind.config.js`
no longer exists (v4 is CSS-first — theme tokens and the `@custom-variant dark`
class strategy live directly in `index.css`).

**React 18, and a ref-forwarding gotcha.** The CLI's generated components
assume React 19, where plain function components can receive a `ref` prop
directly. This project is still on React 18.3 (pinned for ecosystem
compatibility), where that silently fails — a `ref` handed to a non-
`forwardRef` function component is dropped with a console warning, not an
error. This is invisible until something actually depends on the ref: it
surfaced as `Input`/`Textarea` refusing to hold values under
`react-hook-form`'s `register()` (RHF reads the DOM node via ref, not
controlled state) and `Button` losing its ref inside `asChild` compositions
like `SheetTrigger`. Fixed by wrapping `Button`, `Input`, and `Textarea` in
`React.forwardRef`. Other generated primitives (`Select`, `Dialog`, `Tabs`,
etc.) have the same latent gap but haven't needed a ref in this app yet —
apply the same fix if one starts misbehaving.
