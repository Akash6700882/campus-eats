import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { reportApi } from "@/api/report";
import { apiErrorMessage } from "@/lib/api";
import type { ReportExportFormat, ReportPeriod } from "@/types";

export function useReport(period: ReportPeriod) {
  return useQuery({ queryKey: ["admin", "reports", period], queryFn: () => reportApi.get(period) });
}

export function useDownloadReport() {
  return useMutation({
    mutationFn: ({ period, format }: { period: ReportPeriod; format: ReportExportFormat }) =>
      reportApi.download(period, format),
    onError: (err) => toast.error(apiErrorMessage(err, "Could not export the report")),
  });
}
