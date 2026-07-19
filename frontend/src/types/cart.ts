export interface CartItem {
  id: string;
  food_id: string;
  food_name: string;
  unit_price: number;
  quantity: number;
  subtotal: number;
  image_url: string | null;
  is_available: boolean;
}

export interface CartSummary {
  items: CartItem[];
  item_total: number;
  discount_amount: number;
  delivery_charge: number;
  packing_charge: number;
  gst_amount: number;
  grand_total: number;
  estimated_delivery_minutes: number;
  coupon_code: string | null;
  coupon_error: string | null;
}
