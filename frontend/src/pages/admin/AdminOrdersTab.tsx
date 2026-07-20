import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { PageSpinner } from "@/components/PageSpinner";
import { useAdminDeliveryPartners, useAdminOrderActions, useAdminOrders } from "@/hooks/useAdmin";
import { formatCurrency, formatDateTime, ORDER_STATUS_LABELS } from "@/lib/format";
import { ORDER_STATUSES } from "@/types";
import type { Order, OrderStatus } from "@/types";

export function AdminOrdersTab() {
  const [statusFilter, setStatusFilter] = useState<OrderStatus | "all">("all");
  const { data: orders, isLoading } = useAdminOrders(statusFilter === "all" ? undefined : statusFilter);
  const { data: partners } = useAdminDeliveryPartners();
  const { cancel, assignPartner } = useAdminOrderActions();

  const [cancelTarget, setCancelTarget] = useState<Order | null>(null);
  const [reason, setReason] = useState("");
  const [assignTarget, setAssignTarget] = useState<Order | null>(null);

  const availablePartners = partners?.filter((p) => p.is_available) ?? [];

  return (
    <div>
      <div className="mb-4 flex items-center gap-2">
        <Select value={statusFilter} onValueChange={(v) => setStatusFilter(v as OrderStatus | "all")}>
          <SelectTrigger className="w-48">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {ORDER_STATUSES.map((s) => (
              <SelectItem key={s} value={s}>
                {ORDER_STATUS_LABELS[s]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : !orders || orders.length === 0 ? (
        <p className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
          No orders match this filter.
        </p>
      ) : (
        <div className="space-y-2">
          {orders.map((order) => {
            const cancellable = !["delivered", "cancelled", "refunded"].includes(order.status);
            const needsAssignment = order.status === "ready" && !order.delivery_partner;
            return (
              <Card key={order.id}>
                <CardContent className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
                  <div>
                    <p className="font-medium">{order.order_number}</p>
                    <p className="text-xs text-muted-foreground">
                      {order.customer_name} &middot; {formatDateTime(order.created_at)}
                    </p>
                  </div>
                  <p className="text-muted-foreground">{formatCurrency(order.grand_total)}</p>
                  <Badge variant="secondary">{ORDER_STATUS_LABELS[order.status]}</Badge>
                  <div className="flex gap-2">
                    {needsAssignment && (
                      <Button size="sm" variant="outline" onClick={() => setAssignTarget(order)}>
                        Assign partner
                      </Button>
                    )}
                    {cancellable && (
                      <Button size="sm" variant="outline" onClick={() => setCancelTarget(order)}>
                        Cancel
                      </Button>
                    )}
                  </div>
                </CardContent>
              </Card>
            );
          })}
        </div>
      )}

      <Dialog open={!!cancelTarget} onOpenChange={(open) => !open && setCancelTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cancel order {cancelTarget?.order_number}</DialogTitle>
          </DialogHeader>
          <Textarea placeholder="Reason (optional)" value={reason} onChange={(e) => setReason(e.target.value)} />
          <DialogFooter>
            <Button variant="outline" onClick={() => setCancelTarget(null)}>
              Back
            </Button>
            <Button
              variant="destructive"
              disabled={cancel.isPending}
              onClick={() =>
                cancelTarget &&
                cancel.mutate(
                  { orderId: cancelTarget.id, reason: reason || undefined },
                  { onSuccess: () => setCancelTarget(null) },
                )
              }
            >
              {cancel.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Cancel order
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={!!assignTarget} onOpenChange={(open) => !open && setAssignTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Assign a delivery partner — {assignTarget?.order_number}</DialogTitle>
          </DialogHeader>
          {availablePartners.length === 0 ? (
            <p className="text-sm text-muted-foreground">No available delivery partners right now.</p>
          ) : (
            <div className="space-y-2">
              {availablePartners.map((partner) => (
                <Button
                  key={partner.id}
                  variant="outline"
                  className="w-full justify-start"
                  disabled={assignPartner.isPending}
                  onClick={() =>
                    assignTarget &&
                    assignPartner.mutate(
                      { orderId: assignTarget.id, partnerId: partner.id },
                      { onSuccess: () => setAssignTarget(null) },
                    )
                  }
                >
                  {partner.full_name} {partner.vehicle_number && `— ${partner.vehicle_number}`}
                </Button>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
