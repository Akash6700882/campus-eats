import { api } from "@/lib/api";
import type { Address, AddressInput } from "@/types";

export const addressesApi = {
  list: () => api.get<Address[]>("/addresses").then((r) => r.data),
  create: (payload: AddressInput) => api.post<Address>("/addresses", payload).then((r) => r.data),
  update: (id: string, payload: Partial<AddressInput>) =>
    api.patch<Address>(`/addresses/${id}`, payload).then((r) => r.data),
  remove: (id: string) => api.delete(`/addresses/${id}`),
};
