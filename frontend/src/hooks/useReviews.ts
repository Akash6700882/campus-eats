import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { reviewsApi } from "@/api/reviews";
import { apiErrorMessage } from "@/lib/api";
import type { ReviewCreateInput } from "@/types";

export function useFoodReviews(foodId: string, enabled = true) {
  return useQuery({
    queryKey: ["reviews", foodId],
    queryFn: () => reviewsApi.listForFood(foodId),
    enabled,
  });
}

export function useReviewActions(foodId: string) {
  const queryClient = useQueryClient();
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["reviews", foodId] });
    queryClient.invalidateQueries({ queryKey: ["foods"] });
  };

  const create = useMutation({
    mutationFn: (payload: ReviewCreateInput) => reviewsApi.create(foodId, payload),
    onSuccess: () => {
      invalidate();
      toast.success("Thanks for your review!");
    },
    onError: (err) => toast.error(apiErrorMessage(err, "Could not submit review")),
  });

  const toggleLike = useMutation({
    mutationFn: (reviewId: string) => reviewsApi.toggleLike(reviewId),
    onSuccess: invalidate,
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const remove = useMutation({
    mutationFn: (reviewId: string) => reviewsApi.remove(reviewId),
    onSuccess: () => {
      invalidate();
      toast.success("Review deleted");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  return { create, toggleLike, remove };
}
