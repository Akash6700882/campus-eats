import { api } from "@/lib/api";
import type { Order, PaymentInitiateResponse, PaymentResponse, PaymentVerifyRequest } from "@/types";

export const paymentsApi = {
  initiate: (orderId: string) =>
    api.post<PaymentInitiateResponse>(`/orders/${orderId}/payment/initiate`).then((r) => r.data),
  verify: (orderId: string, payload: PaymentVerifyRequest) =>
    api.post<PaymentResponse>(`/orders/${orderId}/payment/verify`, payload).then((r) => r.data),
  cancel: (orderId: string) => api.post<Order>(`/orders/${orderId}/payment/cancel`).then((r) => r.data),
  downloadInvoice: async (orderId: string, orderNumber: string) => {
    const response = await api.get(`/orders/${orderId}/invoice`, { responseType: "blob" });
    const url = URL.createObjectURL(response.data as Blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `${orderNumber}.pdf`;
    link.click();
    URL.revokeObjectURL(url);
  },
};
