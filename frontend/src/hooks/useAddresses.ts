import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { addressesApi } from "@/api/addresses";
import { apiErrorMessage } from "@/lib/api";
import { useAuth } from "@/store/auth";
import type { AddressInput } from "@/types";

export const addressesQueryKey = ["addresses"] as const;

export function useAddresses() {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: addressesQueryKey,
    queryFn: addressesApi.list,
    enabled: isAuthenticated,
  });
}

export function useAddressMutations() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: addressesQueryKey });

  const create = useMutation({
    mutationFn: (payload: AddressInput) => addressesApi.create(payload),
    onSuccess: invalidate,
    onError: (err) => toast.error(apiErrorMessage(err, "Could not save address")),
  });

  const remove = useMutation({
    mutationFn: (id: string) => addressesApi.remove(id),
    onSuccess: invalidate,
    onError: (err) => toast.error(apiErrorMessage(err, "Could not remove address")),
  });

  return { create, remove };
}
