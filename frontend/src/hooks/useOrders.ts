import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { ordersApi } from "@/api/orders";
import { apiErrorMessage } from "@/lib/api";
import { useAuth } from "@/store/auth";

export function useOrders() {
  const { isAuthenticated } = useAuth();
  return useQuery({ queryKey: ["orders"], queryFn: ordersApi.list, enabled: isAuthenticated });
}

export function useOrder(orderId: string | undefined) {
  return useQuery({
    queryKey: ["orders", orderId],
    queryFn: () => ordersApi.get(orderId as string),
    enabled: !!orderId,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      const active = status && !["delivered", "cancelled", "refunded"].includes(status);
      return active ? 15_000 : false;
    },
  });
}

export function useCancelOrder(orderId: string) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: () => ordersApi.cancel(orderId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["orders", orderId] });
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      toast.success("Order cancelled");
    },
    onError: (err) => toast.error(apiErrorMessage(err, "Could not cancel order")),
  });
}
