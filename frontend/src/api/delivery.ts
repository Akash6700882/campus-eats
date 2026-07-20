import { api } from "@/lib/api";
import type { DeliveryLocationUpdate, DeliveryPartner, Order } from "@/types";

export const deliveryApi = {
  getMe: () => api.get<DeliveryPartner>("/delivery/me").then((r) => r.data),
  updateLocation: (payload: DeliveryLocationUpdate) =>
    api.patch<DeliveryPartner>("/delivery/me/location", payload).then((r) => r.data),
  listOrders: () => api.get<Order[]>("/delivery/orders").then((r) => r.data),
  pickup: (orderId: string) => api.post<Order>(`/delivery/orders/${orderId}/pickup`).then((r) => r.data),
  onTheWay: (orderId: string) => api.post<Order>(`/delivery/orders/${orderId}/on-the-way`).then((r) => r.data),
  deliver: (orderId: string, otp: string) =>
    api.post<Order>(`/delivery/orders/${orderId}/deliver`, { otp }).then((r) => r.data),
};
