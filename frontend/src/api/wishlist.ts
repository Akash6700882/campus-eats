import { api } from "@/lib/api";
import type { WishlistItem } from "@/types";

export const wishlistApi = {
  list: () => api.get<WishlistItem[]>("/wishlist").then((r) => r.data),
  add: (foodId: string) => api.post<WishlistItem>(`/wishlist/${foodId}`).then((r) => r.data),
  remove: (foodId: string) => api.delete(`/wishlist/${foodId}`),
};
