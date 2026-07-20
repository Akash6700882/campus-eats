export interface OrderStatusCount {
  status: string;
  count: number;
}

export interface DailyRevenue {
  date: string;
  revenue: number;
  order_count: number;
}

export interface BestSellingFood {
  name: string;
  quantity_sold: number;
  revenue: number;
}

export interface AnalyticsSummary {
  total_orders: number;
  total_revenue: number;
  total_customers: number;
  total_delivery_partners: number;
  orders_by_status: OrderStatusCount[];
  revenue_last_7_days: DailyRevenue[];
  best_selling_foods: BestSellingFood[];
}
