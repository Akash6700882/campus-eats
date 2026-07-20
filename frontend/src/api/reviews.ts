import { api } from "@/lib/api";
import type { Review, ReviewCreateInput, ReviewLikeResult } from "@/types";

export const reviewsApi = {
  listForFood: (foodId: string) => api.get<Review[]>(`/foods/${foodId}/reviews`).then((r) => r.data),
  create: (foodId: string, payload: ReviewCreateInput) =>
    api.post<Review>(`/foods/${foodId}/reviews`, payload).then((r) => r.data),
  remove: (reviewId: string) => api.delete(`/reviews/${reviewId}`),
  toggleLike: (reviewId: string) =>
    api.post<ReviewLikeResult>(`/reviews/${reviewId}/like`).then((r) => r.data),
};
