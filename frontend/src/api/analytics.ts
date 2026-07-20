import { api } from "@/lib/api";
import type { AnalyticsSummary } from "@/types";

export const analyticsApi = {
  summary: () => api.get<AnalyticsSummary>("/admin/analytics/summary").then((r) => r.data),
};
