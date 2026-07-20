import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { kitchenApi } from "@/api/kitchen";
import { apiErrorMessage } from "@/lib/api";

export const kitchenOrdersKey = ["kitchen", "orders"] as const;

export function useKitchenOrders() {
  return useQuery({ queryKey: kitchenOrdersKey, queryFn: kitchenApi.listOrders, refetchInterval: 20_000 });
}

export function useKitchenActions() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: kitchenOrdersKey });

  const accept = useMutation({
    mutationFn: (orderId: string) => kitchenApi.accept(orderId),
    onSuccess: invalidate,
    onError: (err) => toast.error(apiErrorMessage(err)),
  });
  const reject = useMutation({
    mutationFn: ({ orderId, reason }: { orderId: string; reason?: string }) => kitchenApi.reject(orderId, reason),
    onSuccess: () => {
      invalidate();
      toast.success("Order rejected");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });
  const startPreparing = useMutation({
    mutationFn: (orderId: string) => kitchenApi.startPreparing(orderId),
    onSuccess: invalidate,
    onError: (err) => toast.error(apiErrorMessage(err)),
  });
  const markReady = useMutation({
    mutationFn: (orderId: string) => kitchenApi.markReady(orderId),
    onSuccess: (order) => {
      invalidate();
      toast.success(order.delivery_partner ? "Ready — delivery partner assigned" : "Marked ready");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  return { accept, reject, startPreparing, markReady };
}
