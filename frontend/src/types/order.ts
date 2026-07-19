import type { Address } from "./address";

export const ORDER_STATUSES = [
  "pending",
  "accepted",
  "preparing",
  "ready",
  "assigned",
  "picked_up",
  "on_the_way",
  "delivered",
  "cancelled",
  "refunded",
] as const;

export type OrderStatus = (typeof ORDER_STATUSES)[number];

export const ACTIVE_ORDER_STATUSES: OrderStatus[] = [
  "pending",
  "accepted",
  "preparing",
  "ready",
  "assigned",
  "picked_up",
  "on_the_way",
];

export interface OrderItem {
  food_id: string;
  food_name: string;
  unit_price: number;
  quantity: number;
  subtotal: number;
}

export interface DeliveryPartnerBrief {
  id: string;
  full_name: string;
  phone: string;
  vehicle_number: string | null;
  current_latitude: number | null;
  current_longitude: number | null;
}

export interface Order {
  id: string;
  order_number: string;
  status: OrderStatus;
  items: OrderItem[];
  item_total: number;
  discount_amount: number;
  delivery_charge: number;
  packing_charge: number;
  gst_amount: number;
  grand_total: number;
  estimated_delivery_minutes: number;
  notes: string | null;
  delivery_otp: string | null;
  placed_at: string | null;
  delivered_at: string | null;
  cancelled_at: string | null;
  created_at: string;
  customer_name: string;
  customer_phone: string;
  address: Address;
  delivery_partner: DeliveryPartnerBrief | null;
}

export interface CheckoutRequest {
  address_id: string;
  coupon_code?: string | null;
  notes?: string | null;
}
