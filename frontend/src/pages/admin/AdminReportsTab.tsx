import { useState } from "react";
import { Download, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageSpinner } from "@/components/PageSpinner";
import { useDownloadReport, useReport } from "@/hooks/useReport";
import { formatCurrency } from "@/lib/format";
import type { ReportExportFormat, ReportPeriod } from "@/types";

const PERIODS: { value: ReportPeriod; label: string }[] = [
  { value: "daily", label: "Daily (last 24h)" },
  { value: "weekly", label: "Weekly (last 7 days)" },
  { value: "monthly", label: "Monthly (last 30 days)" },
  { value: "yearly", label: "Yearly (last 365 days)" },
];

const EXPORT_FORMATS: { value: ReportExportFormat; label: string }[] = [
  { value: "csv", label: "CSV" },
  { value: "excel", label: "Excel" },
  { value: "pdf", label: "PDF" },
];

export function AdminReportsTab() {
  const [period, setPeriod] = useState<ReportPeriod>("weekly");
  const { data: report, isLoading } = useReport(period);
  const download = useDownloadReport();

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <Select value={period} onValueChange={(v) => setPeriod(v as ReportPeriod)}>
          <SelectTrigger className="w-56">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {PERIODS.map((p) => (
              <SelectItem key={p.value} value={p.value}>
                {p.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="flex gap-2">
          {EXPORT_FORMATS.map((f) => (
            <Button
              key={f.value}
              size="sm"
              variant="outline"
              disabled={download.isPending}
              onClick={() => download.mutate({ period, format: f.value })}
            >
              {download.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Download className="h-4 w-4" />}
              {f.label}
            </Button>
          ))}
        </div>
      </div>

      {isLoading || !report ? (
        <PageSpinner />
      ) : (
        <>
          <div className="grid gap-4 sm:grid-cols-2">
            <Card>
              <CardContent className="py-4">
                <p className="text-xs text-muted-foreground">Total orders</p>
                <p className="font-heading text-xl font-bold">{report.total_orders}</p>
                <p className="text-xs text-muted-foreground">
                  {report.start_date} to {report.end_date}
                </p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="py-4">
                <p className="text-xs text-muted-foreground">Total revenue (delivered orders)</p>
                <p className="font-heading text-xl font-bold">{formatCurrency(report.total_revenue)}</p>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardContent className="space-y-2 py-4">
              <p className="font-heading text-sm font-semibold">Orders by status</p>
              {report.orders_by_status.length === 0 ? (
                <p className="text-sm text-muted-foreground">No orders in this period.</p>
              ) : (
                <div className="flex flex-wrap gap-2">
                  {report.orders_by_status.map((row) => (
                    <Badge key={row.status} variant="secondary" className="capitalize">
                      {row.status.replace(/_/g, " ")}: {row.count}
                    </Badge>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="space-y-2 py-4">
              <p className="font-heading text-sm font-semibold">Best-selling foods</p>
              {report.best_selling_foods.length === 0 ? (
                <p className="text-sm text-muted-foreground">No delivered orders in this period yet.</p>
              ) : (
                <div className="space-y-1 text-sm">
                  {report.best_selling_foods.map((row) => (
                    <div key={row.name} className="flex justify-between text-muted-foreground">
                      <span>
                        {row.name} &times; {row.quantity_sold}
                      </span>
                      <span>{formatCurrency(row.revenue)}</span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="space-y-2 py-4">
              <p className="font-heading text-sm font-semibold">Daily breakdown</p>
              {report.daily_breakdown.length === 0 ? (
                <p className="text-sm text-muted-foreground">No delivered orders in this period yet.</p>
              ) : (
                <div className="space-y-1 text-sm">
                  {report.daily_breakdown.map((row) => (
                    <div key={row.date} className="flex justify-between text-muted-foreground">
                      <span>{row.date}</span>
                      <span>
                        {formatCurrency(row.revenue)} &middot; {row.order_count} orders
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}
