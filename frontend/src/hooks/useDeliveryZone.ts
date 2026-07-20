import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { deliveryZoneApi } from "@/api/deliveryZone";
import { apiErrorMessage } from "@/lib/api";
import type { DeliveryZoneUpdateInput } from "@/types";

export const deliveryZoneKey = ["delivery-zone"] as const;

export function useDeliveryZone() {
  return useQuery({ queryKey: deliveryZoneKey, queryFn: deliveryZoneApi.get });
}

export function useUpdateDeliveryZone() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DeliveryZoneUpdateInput) => deliveryZoneApi.update(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: deliveryZoneKey });
      toast.success("Delivery zone updated");
    },
    onError: (err) => toast.error(apiErrorMessage(err, "Could not update the delivery zone")),
  });
}
