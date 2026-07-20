import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { adminApi } from "@/api/admin";
import { adminMenuApi } from "@/api/menu";
import { apiErrorMessage } from "@/lib/api";
import type {
  CategoryInput,
  DeliveryPartnerCreateInput,
  FoodInput,
  OrderStatus,
} from "@/types";

export const adminOrdersKey = ["admin", "orders"] as const;
export const adminPartnersKey = ["admin", "delivery-partners"] as const;

export function useAdminOrders(status?: OrderStatus) {
  return useQuery({
    queryKey: [...adminOrdersKey, status ?? "all"],
    queryFn: () => adminApi.listOrders(status),
    refetchInterval: 20_000,
  });
}

export function useAdminDeliveryPartners() {
  return useQuery({ queryKey: adminPartnersKey, queryFn: adminApi.listDeliveryPartners });
}

export function useDeliveryRoleUsers(enabled: boolean) {
  return useQuery({
    queryKey: ["admin", "users", "delivery"],
    queryFn: () => adminApi.listUsersByRole("delivery"),
    enabled,
  });
}

export function useAdminOrderActions() {
  const queryClient = useQueryClient();
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: adminOrdersKey });
    queryClient.invalidateQueries({ queryKey: adminPartnersKey });
  };

  const cancel = useMutation({
    mutationFn: ({ orderId, reason }: { orderId: string; reason?: string }) => adminApi.cancelOrder(orderId, reason),
    onSuccess: () => {
      invalidate();
      toast.success("Order cancelled");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const assignPartner = useMutation({
    mutationFn: ({ orderId, partnerId }: { orderId: string; partnerId: string }) =>
      adminApi.assignPartner(orderId, partnerId),
    onSuccess: () => {
      invalidate();
      toast.success("Delivery partner assigned");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  return { cancel, assignPartner };
}

export function useCreateDeliveryPartner() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: DeliveryPartnerCreateInput) => adminApi.createDeliveryPartner(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: adminPartnersKey });
      toast.success("Delivery partner profile created");
    },
    onError: (err) => toast.error(apiErrorMessage(err, "Could not create delivery partner")),
  });
}

export function useAdminMenuActions() {
  const queryClient = useQueryClient();
  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["categories"] });
    queryClient.invalidateQueries({ queryKey: ["foods"] });
  };

  const createCategory = useMutation({
    mutationFn: (payload: CategoryInput) => adminMenuApi.createCategory(payload),
    onSuccess: () => {
      invalidate();
      toast.success("Category created");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const deleteCategory = useMutation({
    mutationFn: (id: string) => adminMenuApi.deleteCategory(id),
    onSuccess: () => {
      invalidate();
      toast.success("Category deleted");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const createFood = useMutation({
    mutationFn: (payload: FoodInput) => adminMenuApi.createFood(payload),
    onSuccess: () => {
      invalidate();
      toast.success("Food item created");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const updateFood = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: Partial<FoodInput> }) => adminMenuApi.updateFood(id, payload),
    onSuccess: () => {
      invalidate();
      toast.success("Food item updated");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  const deleteFood = useMutation({
    mutationFn: (id: string) => adminMenuApi.deleteFood(id),
    onSuccess: () => {
      invalidate();
      toast.success("Food item deleted");
    },
    onError: (err) => toast.error(apiErrorMessage(err)),
  });

  return { createCategory, deleteCategory, createFood, updateFood, deleteFood };
}
