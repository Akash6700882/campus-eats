import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { wishlistApi } from "@/api/wishlist";
import { apiErrorMessage } from "@/lib/api";
import { useAuth } from "@/store/auth";

export const wishlistQueryKey = ["wishlist"] as const;

export function useWishlist() {
  const { isAuthenticated } = useAuth();
  return useQuery({ queryKey: wishlistQueryKey, queryFn: wishlistApi.list, enabled: isAuthenticated });
}

export function useWishlistMutations() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: wishlistQueryKey });

  const add = useMutation({
    mutationFn: (foodId: string) => wishlistApi.add(foodId),
    onSuccess: () => {
      invalidate();
      toast.success("Added to wishlist");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const remove = useMutation({
    mutationFn: (foodId: string) => wishlistApi.remove(foodId),
    onSuccess: invalidate,
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  return { add, remove };
}
