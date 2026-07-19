import { api } from "@/lib/api";
import type { CheckoutRequest, Order } from "@/types";

export const ordersApi = {
  checkout: (payload: CheckoutRequest) => api.post<Order>("/orders", payload).then((r) => r.data),
  list: () => api.get<Order[]>("/orders").then((r) => r.data),
  get: (id: string) => api.get<Order>(`/orders/${id}`).then((r) => r.data),
  cancel: (id: string) => api.post<Order>(`/orders/${id}/cancel`).then((r) => r.data),
};
