import { api } from "@/lib/api";
import type { Order } from "@/types";

export const kitchenApi = {
  listOrders: () => api.get<Order[]>("/kitchen/orders").then((r) => r.data),
  accept: (orderId: string) => api.post<Order>(`/kitchen/orders/${orderId}/accept`).then((r) => r.data),
  reject: (orderId: string, reason?: string) =>
    api.post<Order>(`/kitchen/orders/${orderId}/reject`, { reason }).then((r) => r.data),
  startPreparing: (orderId: string) =>
    api.post<Order>(`/kitchen/orders/${orderId}/start-preparing`).then((r) => r.data),
  markReady: (orderId: string) => api.post<Order>(`/kitchen/orders/${orderId}/ready`).then((r) => r.data),
};
