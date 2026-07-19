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

### Phase 6 — Staff order lifecycle & live tracking *(current)*
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

## Not started yet

- **Reviews, wishlist, notifications API** — models exist (`Review`,
  `ReviewLike`, `WishlistItem`, `Notification`), no service/router yet.
- **Admin analytics dashboard** — revenue/order charts, best-sellers,
  customer/delivery-partner management UI, monthly/yearly reports.
- **Frontend** — `frontend/src` is still the unmodified Vite scaffold
  (`main.tsx`, `App.tsx`, `index.css`). No pages, components, or API
  integration exist yet, for any of the four roles.
- **Deployment** — Dockerfiles and docker-compose exist for local dev; no
  CI workflow content beyond the `.github/workflows/` folder shell, no
  Vercel/Render/Railway config, no Postman collection.

## Known gaps / accepted trade-offs

- Delivery partner "nearest" assignment uses haversine distance on the
  partner's last-reported lat/lng, not real-time routing — fine at campus
  scale, would need a routing API for anything larger.
- WebSocket fan-out is in-process only (see above) — a real multi-worker
  deployment needs Redis pub/sub or similar wired into `app/ws/manager.py`.
