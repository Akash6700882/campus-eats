import { api } from "@/lib/api";
import type { CartSummary } from "@/types";

export const cartApi = {
  get: (couponCode?: string) =>
    api.get<CartSummary>("/cart", { params: couponCode ? { coupon_code: couponCode } : {} }).then((r) => r.data),
  addItem: (food_id: string, quantity = 1) =>
    api.post<CartSummary>("/cart/items", { food_id, quantity }).then((r) => r.data),
  updateQuantity: (food_id: string, quantity: number) =>
    api.patch<CartSummary>(`/cart/items/${food_id}`, { quantity }).then((r) => r.data),
  removeItem: (food_id: string) => api.delete<CartSummary>(`/cart/items/${food_id}`).then((r) => r.data),
};
