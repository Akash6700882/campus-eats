import { Link } from "react-router-dom";
import { PackageOpen } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { PageSpinner } from "@/components/PageSpinner";
import { useOrders } from "@/hooks/useOrders";
import { formatCurrency, formatDateTime, ORDER_STATUS_LABELS } from "@/lib/format";
import type { OrderStatus } from "@/types";

const STATUS_VARIANT: Record<OrderStatus, "default" | "secondary" | "destructive" | "outline"> = {
  pending: "outline",
  accepted: "secondary",
  preparing: "secondary",
  ready: "secondary",
  assigned: "secondary",
  picked_up: "secondary",
  on_the_way: "default",
  delivered: "default",
  cancelled: "destructive",
  refunded: "destructive",
};

export function OrderHistoryPage() {
  const { data: orders, isLoading } = useOrders();

  if (isLoading) return <PageSpinner />;

  if (!orders || orders.length === 0) {
    return (
      <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
        <PackageOpen className="h-10 w-10 text-muted-foreground" />
        <h1 className="font-heading text-xl font-bold">No orders yet</h1>
        <p className="text-sm text-muted-foreground">Your order history will show up here.</p>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <h1 className="font-heading text-2xl font-bold">My orders</h1>
      <div className="mt-6 space-y-3">
        {orders.map((order) => (
          <Link key={order.id} to={`/orders/${order.id}`}>
            <Card className="transition-colors hover:bg-accent/40">
              <CardContent className="flex flex-wrap items-center justify-between gap-2 py-4">
                <div>
                  <p className="font-medium">{order.order_number}</p>
                  <p className="text-xs text-muted-foreground">{formatDateTime(order.created_at)}</p>
                  <p className="text-xs text-muted-foreground">
                    {order.items.length} item{order.items.length > 1 ? "s" : ""} &middot; {formatCurrency(order.grand_total)}
                  </p>
                </div>
                <Badge variant={STATUS_VARIANT[order.status]}>{ORDER_STATUS_LABELS[order.status]}</Badge>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}
