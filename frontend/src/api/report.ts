import { api } from "@/lib/api";
import type { Report, ReportExportFormat, ReportPeriod } from "@/types";

export const reportApi = {
  get: (period: ReportPeriod) =>
    api.get<Report>("/admin/reports", { params: { period } }).then((r) => r.data),

  download: async (period: ReportPeriod, format: ReportExportFormat) => {
    const response = await api.get("/admin/reports", {
      params: { period, format },
      responseType: "blob",
    });
    const disposition: string = response.headers["content-disposition"] ?? "";
    const match = /filename="?([^"]+)"?/.exec(disposition);
    const filename = match?.[1] ?? `campus-eats-report-${period}.${format}`;

    const url = URL.createObjectURL(response.data as Blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
  },
};
