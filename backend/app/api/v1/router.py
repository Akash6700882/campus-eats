from fastapi import APIRouter

from app.api.v1.addresses import router as addresses_router
from app.api.v1.admin_orders import router as admin_orders_router
from app.api.v1.auth import router as auth_router
from app.api.v1.cart import router as cart_router
from app.api.v1.coupons import router as coupons_router
from app.api.v1.delivery import router as delivery_router
from app.api.v1.kitchen import router as kitchen_router
from app.api.v1.menu import router as menu_router
from app.api.v1.orders import router as orders_router
from app.api.v1.payments import router as payments_router
from app.api.v1.ws import router as ws_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(menu_router)
api_router.include_router(addresses_router)
api_router.include_router(cart_router)
api_router.include_router(orders_router)
api_router.include_router(coupons_router)
api_router.include_router(payments_router)
api_router.include_router(kitchen_router)
api_router.include_router(delivery_router)
api_router.include_router(admin_orders_router)
api_router.include_router(ws_router)
