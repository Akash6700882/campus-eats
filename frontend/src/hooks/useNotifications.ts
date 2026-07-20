import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { notificationsApi } from "@/api/notifications";
import { useAuth } from "@/store/auth";

export const notificationsQueryKey = ["notifications"] as const;

export function useNotifications() {
  const { isAuthenticated } = useAuth();
  return useQuery({
    queryKey: notificationsQueryKey,
    queryFn: notificationsApi.list,
    enabled: isAuthenticated,
    refetchInterval: 30_000,
  });
}

export function useNotificationActions() {
  const queryClient = useQueryClient();
  const invalidate = () => queryClient.invalidateQueries({ queryKey: notificationsQueryKey });

  const markRead = useMutation({
    mutationFn: (id: string) => notificationsApi.markRead(id),
    onSuccess: invalidate,
  });

  const markAllRead = useMutation({
    mutationFn: () => notificationsApi.markAllRead(),
    onSuccess: invalidate,
  });

  return { markRead, markAllRead };
}
