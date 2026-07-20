# Progress

Tracks what's actually implemented, phase by phase. Updated as work lands — this
is the source of truth, not the aspirational feature list in the original brief.

## Done

### Phase 1 — Foundation
- SQLAlchemy 2.0 models for all 17 tables, migrated via Alembic.
- JWT auth: signup, login, OTP login, refresh, forgot/reset password. Role-based
  access control (`customer` / `admin` / `kitchen` / `delivery`) via `require_role`.
- Idempotent seed script (`backend/scripts/seed.py`): roles, default admin,
  7 categories / 21 sample foods, placeholder campus geofence polygon.
- Rate limiting (slowapi), security headers middleware, CORS.

### Phase 2 — Menu
- Public browse/search (`/categories`, `/foods` — filter by query, category,
  price range, rating, veg/non-veg, popular, today's special).
- Admin CRUD for categories and foods, Cloudinary image upload.

### Phase 3 — Cart & coupons
- Server-persisted per-user cart with live pricing.
- Coupon validation and discount pricing (percent/flat, min order, usage limits).

### Phase 4 — Checkout & orders
- Checkout: cart → order, campus geofence check (point-in-polygon against
  active `DeliveryZone` rows), full price breakdown (item total, discount,
  delivery/packing charge, GST, grand total), order number generation.
- Customer order history, detail view, self-cancel (while still pending/
  accepted/preparing).

### Phase 5 — Payments
- Razorpay integration behind a `PaymentGateway` protocol (swappable for
  tests via a fake gateway).
- Create → pay → verify signature → mark paid; cancel-if-unpaid restores the
  cart; PDF invoice generation.

### Phase 6 — Staff order lifecycle & live tracking
- **Kitchen dashboard API** (`/kitchen/*`): queue of active orders, accept,
  reject (with reason), start preparing, mark ready.
- **Delivery dashboard API** (`/delivery/*`): a delivery-role user's own
  partner profile, live location/availability, assigned-order queue, pickup →
  on-the-way → deliver (OTP-verified), today's earnings / completed-delivery
  count updated on each successful delivery.
- **Auto-assignment**: marking an order ready picks the nearest *available*
  delivery partner by straight-line distance to the delivery address and
  assigns automatically; if none are free, the order stays `ready` and
  unassigned for an admin to assign manually.
- **Admin order oversight** (`/admin/orders`, `/admin/delivery-partners`):
  list/filter all orders, force-cancel an order at any non-terminal status
  (frees up the delivery partner if one was assigned), manually assign a
  delivery partner to an unassigned `ready` order, create delivery-partner
  profiles for `delivery`-role users.
- **Live order tracking over WebSockets** (`/ws/orders/{id}`, `/ws/kitchen`,
  `/ws/delivery`): every state transition above broadcasts to the customer
  tracking their order, the kitchen dashboard, and (once assigned) the
  delivery partner's channel. Token-authenticated via a `?token=` query param
  (browsers can't set custom headers on a WS handshake). Single-process
  in-memory pub/sub — correct for one uvicorn worker; would need Redis
  pub/sub to fan out across multiple replicas.

Full `OrderStatus` state machine (`app/services/order_state_machine.py`):
`pending → accepted → preparing → ready → assigned → picked_up → on_the_way
→ delivered → refunded`, with `cancelled` reachable from the early
customer/kitchen-controlled states and via admin force-cancel from any
non-terminal state.

Test coverage: 100 tests (`backend/tests/`) — unit tests for JWT/security/RBAC/
geofence/WS pub-sub, API tests for every router above including role-gating,
invalid-transition rejection, and the full kitchen → delivery → OTP-delivered
happy path.

### Phase 7 — Customer frontend
React + TypeScript + Vite, Tailwind v4, shadcn/ui (`radix-nova` style, warm
orange food-brand palette, light/dark via a `ThemeProvider` toggling `.dark`
on `<html>`). Covers the full customer journey against the Phase 1–6 APIs:

- **Shell**: sticky `Navbar` (search, live cart-count badge, theme toggle,
  auth-aware menu, mobile `Sheet` nav), `Footer`, `ProtectedRoute` for
  auth-gated pages, axios client with automatic access-token refresh on 401.
- **Auth**: signup and login (password or phone OTP) pages.
- **Home**: hero with search, category chips, "Popular right now" and
  "Today's specials" rows.
- **Menu**: search (debounced), category/veg/rating filters synced to the
  URL, `FoodCard` (image, veg badge, discount, rating, prep time, quantity
  stepper, add-to-cart).
- **Cart**: quantity edit/remove, coupon apply with live-priced preview,
  full charge breakdown.
- **Checkout**: saved-address picker + inline add-address form (campus
  fields, browser-geolocation capture — no Google Maps key needed for the
  core flow), order notes, place order.
- **Payment & tracking** (`/orders/:id`, doubles as the post-checkout
  confirmation page): Razorpay Checkout.js integration (create → pay →
  verify signature), pending-order cancel (restores cart), 8-step status
  timeline, delivery OTP display, delivery-partner card once assigned, live
  updates via the `/ws/orders/{id}` WebSocket (falls back to a 15s poll),
  invoice download.
- **Order history & profile**: past orders with status badges, saved-address
  management, logout.

Verified end-to-end in a real browser against the live backend (signup →
browse → filter → cart → checkout with a captured campus location → order
placed → payment attempt cleanly rejected with placeholder Razorpay test
keys → invoice download → order history → profile) — not just typechecked.

Along the way, found and fixed two identical-shaped ORM bugs where a
freshly-created related row (a `Payment`, a `DeliveryPartner` assignment)
was attached via `session.add()` / a bare FK column instead of the
SQLAlchemy relationship, so an already-loaded parent object in the same
session never saw it (`payment_service.py`, `order_service.py`). Also
hardened `RazorpayGateway.create_order` to turn a Razorpay auth failure
(e.g. this repo's placeholder test keys) into a clean `PaymentError` instead
of an unhandled 500.

### Phase 8 — Staff frontends
Kitchen, delivery, and admin dashboards, wired to the Phase 6 APIs. Staff
users share the customer login page (password or OTP) — `LoginPage` reads
the returned user's role and redirects to `/kitchen`, `/delivery`, or
`/admin` instead of home; `RoleProtectedRoute` guards those routes and the
`Navbar` switches to a stripped-down staff mode (no search/cart/menu, just
a "Dashboard" link) once logged in as non-customer.

- **Kitchen** (`/kitchen`): a 4-column queue (new / accepted / preparing /
  ready) with accept, reject (reason dialog), start-preparing, mark-ready
  actions; shows the assigned delivery partner once auto-assignment fires.
  Customer OTP is never fetched into this view.
- **Delivery** (`/delivery`): today's earnings/deliveries/rating, an
  availability toggle, a "update my location" geolocation button, and the
  assigned-order queue with pickup → start-delivery → confirm-delivery
  (OTP entry dialog) actions.
- **Admin** (`/admin`): three tabs — **Orders** (status-filterable list,
  force-cancel with reason, manual delivery-partner assignment for
  unassigned `ready` orders), **Delivery partners** (roster with
  availability/rating/earnings, create a profile for a `delivery`-role
  user), **Menu** (category/food CRUD reusing the existing admin API).

Added one small backend endpoint to support this: `GET /admin/users?role=`
(`UserRepository.list_by_role`, `AdminUserResponse`) — there was previously
no way for an admin to look up which `delivery`-role users exist to promote
to a delivery-partner profile. Covered by two new tests (role-gating +
happy path); full suite is 102 tests.

Verified functionally end-to-end via direct API calls against the live
backend (not the browser UI this time — the dev browser session had the
user's own real in-progress order in it, so verification used isolated
test accounts and a throwaway order instead of risking that session):
kitchen accept → start-preparing → ready (confirmed auto-assignment),
delivery pickup → on-the-way → deliver with the real OTP fetched from the
customer's own view, delivery-partner stats incrementing correctly after
delivery, and admin list/filter + force-cancel. The dashboard components
themselves reuse the same shadcn primitives (`Card`, `Dialog`, `Select`,
`Switch`, `Badge`) already visually confirmed working in the Phase 7
browser pass, plus a clean `tsc --noEmit`.

### Phase 9 — Reviews, wishlist, notifications, admin analytics, CI *(current)*

**Reviews** (`/foods/{id}/reviews`, `/reviews/{id}`, `/reviews/{id}/like`):
rate 1–5 + optional comment, gated by `OrderRepository.has_delivered_order_with_food`
(you can only review food from an order that actually reached `delivered`),
one review per user per food, like/unlike toggle. Creating or deleting a
review recomputes `Food.rating_avg`/`rating_count` incrementally rather than
re-aggregating. Frontend: a `ReviewsDialog` opened from the star rating on
every `FoodCard`, plus a per-item "rate your order" prompt on the order
tracking page once it's `delivered`.

**Wishlist** (`/wishlist`): add/list/remove, unique on
(user, food). Frontend: heart toggle on `FoodCard`, a `/wishlist` page.

**Notifications** (`/notifications`, `.../read`, `.../read-all`): a
`Notification` row is created for the customer alongside the WebSocket
broadcast on every order-status transition (kitchen accept/reject/prepare/
ready, delivery pickup/on-the-way/deliver, admin force-cancel, customer
self-cancel) — same commit, so the notification and the state change can't
drift apart. Frontend: a bell in the navbar with an unread-count badge,
30s-polled dropdown, mark-read on click.

**Admin analytics** (`/admin/analytics/summary`): total revenue (delivered
orders only) and order count, customer/delivery-partner counts, orders
grouped by status, revenue for the last 7 days, top 5 best-selling foods by
quantity — all plain aggregate SQL (`app/repositories/analytics_repository.py`),
no new tables. Frontend: a new "Analytics" tab in the admin dashboard
(Recharts bar charts — revenue by day in the brand primary hue, orders by
status colored semantically: green for delivered, red for cancelled/
refunded, primary for everything in progress — plus a best-sellers list).

**Tooling that was still missing**: `eslint.config.js` (flat config,
`typescript-eslint` + `eslint-plugin-react-hooks` + `eslint-plugin-react-refresh`)
— found and fixed one real bug it caught (`MenuPage` was calling `setState`
synchronously inside a bare `useEffect` to resync local input state from a
URL param on external changes; replaced with the render-time "adjust state
when a prop changes" pattern React recommends instead of an effect).
A first Vitest slice (27 tests across format/utils/VegBadge/StarRatingInput/
StatusTimeline/ThemeProvider/FoodCard) using mocked hooks rather than a full
provider tree. A GitHub Actions workflow (`.github/workflows/ci.yml`) running
backend pytest+ruff against real Postgres/Redis service containers, and
frontend tsc+eslint+vitest+build, on every push/PR to `main`. A Postman
collection (`docs/postman_collection.json`) generated from the live OpenAPI
schema, organized by tag with collection-level bearer auth.

Backend: 3 new repositories, 2 new services, 4 new routers, 14 new tests
(116 total). One real bug found while wiring wishlist: `WishlistRepository.list_for_user`
eager-loaded `WishlistItem.food` but not `Food.category`, and
`FoodResponse.from_food` reads `food.category.name` — a lazy-load attempt
outside the async context crashed with `MissingGreenlet` the first time a
non-empty wishlist was serialized. Fixed by chaining the `selectinload`.

Verified via the backend test suite (116 passing) and `curl` against the
live API for the endpoints frontend code depends on; UI verification used
`tsc --noEmit` + `eslint` + the new Vitest suite rather than a live browser
pass, for the same shared-session reason as Phase 8.

### Phase 10 — Real campus geofence and Google Maps integration

**Geofence**: the campus `DeliveryZone` was a placeholder square around a
generic Bangalore coordinate. Replaced with the real IIT Guwahati campus
boundary (OSM way `52435139`, 101-point polygon fetched via Nominatim,
cross-checked against Wikipedia's stated campus area — ~661 acres computed
from the polygon vs. ~704 acres from Wikipedia, within 6%). `backend/scripts/seed.py`
now upserts this onto whatever zone is currently active, so re-running it
against an already-seeded dev DB fixes the old placeholder in place rather
than creating a duplicate active zone.

**New `/delivery-zone` endpoints**: `GET /delivery-zone` (public — powers the
checkout map's zone overlay) and `PUT /admin/delivery-zone` (admin-only,
validates the submitted GeoJSON is a well-formed, non-self-intersecting
Polygon via shapely before saving). `DeliveryZoneRepository.get_first_active`
added since there's only ever one "main" active zone. 7 new tests.

**Google Maps JS integration** (`@react-google-maps/api`, already a
dependency, previously unused):
- **Checkout map picker** (`CampusMapPicker`): a draggable-pin map bounded to
  the campus area (`restriction` + `strictBounds`), overlaying the real zone
  polygon, alongside — not replacing — the existing browser-geolocation
  button in `AddressForm`.
- **Admin geofence editor** (new "Delivery zone" tab, `DeliveryZoneEditor`):
  drag existing boundary points to adjust them, or draw an entirely new
  polygon via the Drawing library, then save.
- **Delivery partner live map** (`DeliveryLiveMap` in the delivery
  dashboard): shows the partner's last-reported lat/lng as a marker instead
  of just the raw pair.

All three degrade to a plain text notice instead of crashing when
`VITE_GOOGLE_MAPS_API_KEY` is unset (covered by a Vitest test against the
real current empty-key dev state) — no live-browser pass was possible in
this environment (no Playwright/chromium-cli/Chrome MCP available on
Windows here), so rendering with a real key is unverified; typecheck,
eslint, the full backend (123) and frontend (28) test suites, and a
production build all pass.

### Phase 11 — Razorpay webhook (server-side payment reconciliation)

`POST /payments/webhook`: verifies the `X-Razorpay-Signature` header via
`RazorpayGateway.verify_webhook_signature` (HMAC against
`RAZORPAY_WEBHOOK_SECRET`), then reconciles `Payment.status` from
`payment.captured`/`order.paid` (→ paid) and `payment.failed` (→ failed)
events. Idempotent by design: a payment already marked paid is left
untouched, since the existing client-side verify-signature call (Phase 5)
usually wins the race against the async webhook — this is purely the
fallback for when that client-side call never lands (dropped connection,
closed tab mid-payment). New `PaymentRepository.get_by_provider_order_id`
since payments previously were only ever looked up through their parent
order. 5 new tests (128 total); ruff clean.

**Not yet configured**: `RAZORPAY_WEBHOOK_SECRET` is still a placeholder,
and no webhook is registered in the Razorpay dashboard — both need a
publicly reachable HTTPS URL to point at, which this app doesn't have
until Phase "Deployment" below happens (or a tunnel like ngrok is used
for interim local testing).

## Not started yet

- **Kitchen/delivery/admin frontend for reviews/wishlist/notifications** —
  e.g. no way for an admin to moderate/delete other users' reviews from the
  UI (the `DELETE /reviews/{id}` endpoint only allows the review's own
  author, by design).
- **Deployment** — Dockerfiles and docker-compose exist for local dev and
  now there's a CI workflow, but no actual deploy target is configured
  (Vercel/Render/Railway).
- **Email/push notifications** — the in-app `Notification` feed exists;
  the `EmailService`/SMS provider stubs from Phase 1 aren't wired to order
  events yet (only password-reset emails use `EmailService` today).

## Known gaps / accepted trade-offs

- Delivery partner "nearest" assignment uses haversine distance on the
  partner's last-reported lat/lng, not real-time routing — fine at campus
  scale, would need a routing API for anything larger.
- WebSocket fan-out is in-process only (see above) — a real multi-worker
  deployment needs Redis pub/sub or similar wired into `app/ws/manager.py`.
- The IIT Guwahati geofence polygon is crowd-sourced OSM data, not an
  official surveyed boundary — good for "is this address roughly on
  campus," not survey-grade precision right at the fence line. Admins can
  refine it directly via the new "Delivery zone" admin tab.
- Vitest coverage is a first slice (utilities, several presentational/
  interactive components), not exhaustive — pages with heavy React Query +
  routing + multiple provider dependencies (Checkout, OrderTracking) aren't
  covered yet and would need a fuller test-provider wrapper to be worth it.
- The production frontend bundle is a single ~1.28MB (368KB gzipped) chunk —
  Vite warns about it (recharts + radix-ui + framer-motion + @react-google-maps/api
  all in the main bundle). Works fine at this app's scale; splitting the
  admin analytics chart and map components behind dynamic `import()` would
  be the first thing to reach for if load time on the customer-facing pages
  ever mattered.
