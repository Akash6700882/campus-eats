import { api } from "@/lib/api";
import type { AppSettings, AppSettingsInput } from "@/types";

export const appSettingsApi = {
  get: () => api.get<AppSettings>("/settings").then((r) => r.data),
  update: (payload: AppSettingsInput) => api.put<AppSettings>("/admin/settings", payload).then((r) => r.data),
};
