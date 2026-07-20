import { api } from "@/lib/api";
import type { DeliveryZone, DeliveryZoneUpdateInput } from "@/types";

export const deliveryZoneApi = {
  get: () => api.get<DeliveryZone | null>("/delivery-zone").then((r) => r.data),
  update: (payload: DeliveryZoneUpdateInput) =>
    api.put<DeliveryZone>("/admin/delivery-zone", payload).then((r) => r.data),
};
