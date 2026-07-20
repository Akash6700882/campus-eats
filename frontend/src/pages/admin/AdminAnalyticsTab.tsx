import { Bar, BarChart, CartesianGrid, Cell, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Bike, IndianRupee, ShoppingBag, Users } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { PageSpinner } from "@/components/PageSpinner";
import { useAnalyticsSummary } from "@/hooks/useAnalytics";
import { formatCurrency } from "@/lib/format";
import { ORDER_STATUS_LABELS } from "@/lib/format";

const SUCCESS_STATUSES = new Set(["delivered"]);
const FAILURE_STATUSES = new Set(["cancelled", "refunded"]);

function statusColor(status: string): string {
  if (SUCCESS_STATUSES.has(status)) return "var(--success)";
  if (FAILURE_STATUSES.has(status)) return "var(--destructive)";
  return "var(--primary)";
}

function KpiTile({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <Card>
      <CardContent className="flex items-center gap-3 py-4">
        <span className="flex h-10 w-10 items-center justify-center rounded-full bg-accent">{icon}</span>
        <div>
          <p className="text-xs text-muted-foreground">{label}</p>
          <p className="font-heading text-lg font-bold">{value}</p>
        </div>
      </CardContent>
    </Card>
  );
}

export function AdminAnalyticsTab() {
  const { data, isLoading } = useAnalyticsSummary();

  if (isLoading) return <PageSpinner />;
  if (!data) return null;

  const statusData = data.orders_by_status
    .map((s) => ({ status: s.status, label: ORDER_STATUS_LABELS[s.status] ?? s.status, count: s.count }))
    .sort((a, b) => b.count - a.count);

  const revenueData = data.revenue_last_7_days.map((d) => ({
    date: new Date(d.date).toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
    revenue: d.revenue,
  }));

  const bestSelling = [...data.best_selling_foods].sort((a, b) => b.quantity_sold - a.quantity_sold);

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <KpiTile icon={<IndianRupee className="h-5 w-5 text-accent-foreground" />} label="Total revenue (delivered)" value={formatCurrency(data.total_revenue)} />
        <KpiTile icon={<ShoppingBag className="h-5 w-5 text-accent-foreground" />} label="Total orders" value={String(data.total_orders)} />
        <KpiTile icon={<Users className="h-5 w-5 text-accent-foreground" />} label="Customers" value={String(data.total_customers)} />
        <KpiTile icon={<Bike className="h-5 w-5 text-accent-foreground" />} label="Delivery partners" value={String(data.total_delivery_partners)} />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardContent className="py-4">
            <p className="mb-3 font-heading text-sm font-semibold">Revenue — last 7 days</p>
            {revenueData.length === 0 ? (
              <p className="py-8 text-center text-sm text-muted-foreground">No delivered orders in this window yet.</p>
            ) : (
              <ResponsiveContainer width="100%" height={240}>
                <BarChart data={revenueData} margin={{ left: 0, right: 8, top: 4, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border)" />
                  <XAxis dataKey="date" tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} />
                  <YAxis tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} width={40} />
                  <Tooltip
                    formatter={(value: number) => formatCurrency(value)}
                    contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                  />
                  <Bar dataKey="revenue" fill="var(--primary)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardContent className="py-4">
            <p className="mb-3 font-heading text-sm font-semibold">Orders by status</p>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={statusData} layout="vertical" margin={{ left: 0, right: 16, top: 4, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="var(--border)" />
                <XAxis type="number" tick={{ fontSize: 12, fill: "var(--muted-foreground)" }} axisLine={false} tickLine={false} allowDecimals={false} />
                <YAxis
                  type="category"
                  dataKey="label"
                  width={110}
                  tick={{ fontSize: 12, fill: "var(--muted-foreground)" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip contentStyle={{ background: "var(--popover)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                  {statusData.map((entry) => (
                    <Cell key={entry.status} fill={statusColor(entry.status)} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="py-4">
          <p className="mb-3 font-heading text-sm font-semibold">Best-selling foods (delivered orders)</p>
          {bestSelling.length === 0 ? (
            <p className="py-8 text-center text-sm text-muted-foreground">No delivered orders yet.</p>
          ) : (
            <div className="space-y-2">
              {bestSelling.map((food) => {
                const max = bestSelling[0].quantity_sold || 1;
                return (
                  <div key={food.name} className="flex items-center gap-3 text-sm">
                    <span className="w-32 shrink-0 truncate">{food.name}</span>
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-muted">
                      <div
                        className="h-full rounded-full bg-primary"
                        style={{ width: `${(food.quantity_sold / max) * 100}%` }}
                      />
                    </div>
                    <span className="w-10 shrink-0 text-right text-muted-foreground">{food.quantity_sold}</span>
                    <span className="w-20 shrink-0 text-right font-medium">{formatCurrency(food.revenue)}</span>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
