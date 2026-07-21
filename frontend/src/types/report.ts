import type { BestSellingFood, DailyRevenue, OrderStatusCount } from "./analytics";

export type ReportPeriod = "daily" | "weekly" | "monthly" | "yearly";
export type ReportExportFormat = "csv" | "excel" | "pdf";

export interface Report {
  period: ReportPeriod;
  start_date: string;
  end_date: string;
  total_orders: number;
  total_revenue: number;
  orders_by_status: OrderStatusCount[];
  best_selling_foods: BestSellingFood[];
  daily_breakdown: DailyRevenue[];
}
