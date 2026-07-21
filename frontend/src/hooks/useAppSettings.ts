import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { appSettingsApi } from "@/api/appSettings";
import { apiErrorMessage } from "@/lib/api";
import type { AppSettingsInput } from "@/types";

export const appSettingsKey = ["settings"] as const;

export function useAppSettings() {
  return useQuery({ queryKey: appSettingsKey, queryFn: appSettingsApi.get });
}

export function useUpdateAppSettings() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: AppSettingsInput) => appSettingsApi.update(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: appSettingsKey });
      toast.success("Settings updated");
    },
    onError: (err) => toast.error(apiErrorMessage(err, "Could not update settings")),
  });
}
