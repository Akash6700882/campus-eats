import { api } from "@/lib/api";
import type { AdminUser, DeliveryPartner, DeliveryPartnerCreateInput, Order, OrderStatus, Role } from "@/types";

export const adminApi = {
  listOrders: (status?: OrderStatus) =>
    api.get<Order[]>("/admin/orders", { params: status ? { status } : {} }).then((r) => r.data),
  cancelOrder: (orderId: string, reason?: string) =>
    api.post<Order>(`/admin/orders/${orderId}/cancel`, { reason }).then((r) => r.data),
  assignPartner: (orderId: string, deliveryPartnerId: string) =>
    api
      .post<Order>(`/admin/orders/${orderId}/assign`, { delivery_partner_id: deliveryPartnerId })
      .then((r) => r.data),
  listDeliveryPartners: () => api.get<DeliveryPartner[]>("/admin/delivery-partners").then((r) => r.data),
  createDeliveryPartner: (payload: DeliveryPartnerCreateInput) =>
    api.post<DeliveryPartner>("/admin/delivery-partners", payload).then((r) => r.data),
  listUsersByRole: (role: Role) => api.get<AdminUser[]>("/admin/users", { params: { role } }).then((r) => r.data),
};
