import { useState } from "react";
import { ChefHat, Clock, Loader2, MapPin, Phone } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { PageSpinner } from "@/components/PageSpinner";
import { useKitchenActions, useKitchenOrders } from "@/hooks/useKitchen";
import { formatDateTime } from "@/lib/format";
import type { Order, OrderStatus } from "@/types";

const COLUMNS: { status: OrderStatus; title: string }[] = [
  { status: "pending", title: "New orders" },
  { status: "accepted", title: "Accepted" },
  { status: "preparing", title: "Preparing" },
  { status: "ready", title: "Ready / waiting for pickup" },
];

function OrderCard({ order, onReject }: { order: Order; onReject: (order: Order) => void }) {
  const { accept, startPreparing, markReady } = useKitchenActions();
  const busy = accept.isPending || startPreparing.isPending || markReady.isPending;

  return (
    <Card>
      <CardContent className="space-y-2 py-3 text-sm">
        <div className="flex items-start justify-between">
          <p className="font-medium">{order.order_number}</p>
          <span className="flex items-center gap-1 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" /> {formatDateTime(order.created_at)}
          </span>
        </div>

        <div className="space-y-0.5 text-muted-foreground">
          {order.items.map((item) => (
            <p key={item.food_id}>
              {item.quantity} &times; {item.food_name}
            </p>
          ))}
        </div>

        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <MapPin className="h-3 w-3" />
          {[order.address.hostel, order.address.building, order.address.room_number && `Room ${order.address.room_number}`]
            .filter(Boolean)
            .join(", ") || "No address details"}
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <Phone className="h-3 w-3" /> {order.customer_name} &middot; {order.customer_phone}
        </div>

        <div className="flex gap-2 pt-2">
          {order.status === "pending" && (
            <>
              <Button size="sm" className="flex-1" disabled={busy} onClick={() => accept.mutate(order.id)}>
                {accept.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
                Accept
              </Button>
              <Button size="sm" variant="outline" disabled={busy} onClick={() => onReject(order)}>
                Reject
              </Button>
            </>
          )}
          {order.status === "accepted" && (
            <Button size="sm" className="flex-1" disabled={busy} onClick={() => startPreparing.mutate(order.id)}>
              {startPreparing.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              Start preparing
            </Button>
          )}
          {order.status === "preparing" && (
            <Button size="sm" className="flex-1" disabled={busy} onClick={() => markReady.mutate(order.id)}>
              {markReady.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              Mark ready
            </Button>
          )}
          {order.status === "ready" && (
            <Badge variant={order.delivery_partner ? "default" : "outline"} className="w-full justify-center py-1.5">
              {order.delivery_partner ? `Assigned to ${order.delivery_partner.full_name}` : "Waiting for a delivery partner"}
            </Badge>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function KitchenDashboardPage() {
  const { data: orders, isLoading } = useKitchenOrders();
  const { reject } = useKitchenActions();
  const [rejectTarget, setRejectTarget] = useState<Order | null>(null);
  const [reason, setReason] = useState("");

  if (isLoading) return <PageSpinner />;

  function confirmReject() {
    if (!rejectTarget) return;
    reject.mutate(
      { orderId: rejectTarget.id, reason: reason || undefined },
      { onSuccess: () => setRejectTarget(null) },
    );
  }

  return (
    <div className="container py-8">
      <h1 className="flex items-center gap-2 font-heading text-2xl font-bold">
        <ChefHat className="h-6 w-6 text-primary" /> Kitchen dashboard
      </h1>
      <p className="mt-1 text-sm text-muted-foreground">
        {orders?.length ?? 0} active order{orders?.length === 1 ? "" : "s"}
      </p>

      <div className="mt-6 grid gap-4 lg:grid-cols-4">
        {COLUMNS.map((column) => {
          const columnOrders = orders?.filter((o) => o.status === column.status) ?? [];
          return (
            <div key={column.status} className="space-y-3">
              <h2 className="flex items-center justify-between text-sm font-semibold text-muted-foreground">
                {column.title}
                <Badge variant="secondary">{columnOrders.length}</Badge>
              </h2>
              {columnOrders.length === 0 && (
                <p className="rounded-lg border border-dashed border-border p-4 text-center text-xs text-muted-foreground">
                  Nothing here
                </p>
              )}
              {columnOrders.map((order) => (
                <OrderCard key={order.id} order={order} onReject={setRejectTarget} />
              ))}
            </div>
          );
        })}
      </div>

      <Dialog open={!!rejectTarget} onOpenChange={(open) => !open && setRejectTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject order {rejectTarget?.order_number}</DialogTitle>
          </DialogHeader>
          <Textarea
            placeholder="Reason (optional) — e.g. out of stock"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
          />
          <DialogFooter>
            <Button variant="outline" onClick={() => setRejectTarget(null)}>
              Cancel
            </Button>
            <Button variant="destructive" disabled={reject.isPending} onClick={confirmReject}>
              {reject.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Reject order
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
