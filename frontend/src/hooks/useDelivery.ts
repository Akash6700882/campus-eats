import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { deliveryApi } from "@/api/delivery";
import { apiErrorMessage } from "@/lib/api";
import type { DeliveryLocationUpdate } from "@/types";

export const deliveryMeKey = ["delivery", "me"] as const;
export const deliveryOrdersKey = ["delivery", "orders"] as const;

export function useDeliveryProfile() {
  return useQuery({ queryKey: deliveryMeKey, queryFn: deliveryApi.getMe, retry: false });
}

export function useDeliveryOrders() {
  return useQuery({ queryKey: deliveryOrdersKey, queryFn: deliveryApi.listOrders, refetchInterval: 20_000 });
}

export function useDeliveryActions() {
  const queryClient = useQueryClient();
  const invalidateOrders = () => queryClient.invalidateQueries({ queryKey: deliveryOrdersKey });
  const invalidateProfile = () => queryClient.invalidateQueries({ queryKey: deliveryMeKey });

  const updateLocation = useMutation({
    mutationFn: (payload: DeliveryLocationUpdate) => deliveryApi.updateLocation(payload),
    onSuccess: () => {
      invalidateProfile();
      toast.success("Updated");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const pickup = useMutation({
    mutationFn: (orderId: string) => deliveryApi.pickup(orderId),
    onSuccess: invalidateOrders,
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const onTheWay = useMutation({
    mutationFn: (orderId: string) => deliveryApi.onTheWay(orderId),
    onSuccess: invalidateOrders,
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const deliver = useMutation({
    mutationFn: ({ orderId, otp }: { orderId: string; otp: string }) => deliveryApi.deliver(orderId, otp),
    onSuccess: () => {
      invalidateOrders();
      invalidateProfile();
      toast.success("Delivered!");
    },
    onError: (err) => toast.error(apiErrorMessage(err, "Invalid OTP")),
  });

  return { updateLocation, pickup, onTheWay, deliver };
}
