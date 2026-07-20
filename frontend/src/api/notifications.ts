import { api } from "@/lib/api";
import type { Notification, NotificationList } from "@/types";

export const notificationsApi = {
  list: () => api.get<NotificationList>("/notifications").then((r) => r.data),
  markRead: (id: string) => api.post<Notification>(`/notifications/${id}/read`).then((r) => r.data),
  markAllRead: () => api.post("/notifications/read-all"),
};
