import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { cartApi } from "@/api/cart";
import { apiErrorMessage } from "@/lib/api";
import { useAuth } from "@/store/auth";

export const cartQueryKey = ["cart"] as const;

export function useCart(couponCode?: string) {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: couponCode ? [...cartQueryKey, couponCode] : cartQueryKey,
    queryFn: () => cartApi.get(couponCode),
    enabled: isAuthenticated,
  });
}

export function useCartMutations() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: cartQueryKey });

  const addItem = useMutation({
    mutationFn: ({ foodId, quantity }: { foodId: string; quantity?: number }) => cartApi.addItem(foodId, quantity),
    onSuccess: () => {
      invalidate();
      toast.success("Added to cart");
    },
    onError: (err) => toast.error(apiErrorMessage(err, "Could not add to cart")),
  });

  const updateQuantity = useMutation({
    mutationFn: ({ foodId, quantity }: { foodId: string; quantity: number }) =>
      cartApi.updateQuantity(foodId, quantity),
    onSuccess: invalidate,
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const removeItem = useMutation({
    mutationFn: (foodId: string) => cartApi.removeItem(foodId),
    onSuccess: invalidate,
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  return { addItem, updateQuantity, removeItem };
}
