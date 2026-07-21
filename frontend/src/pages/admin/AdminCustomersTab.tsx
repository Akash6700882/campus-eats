import { useState } from "react";
import { Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { PageSpinner } from "@/components/PageSpinner";
import { useAdminCustomerActions, useAdminCustomers } from "@/hooks/useAdmin";
import { formatCurrency, formatDateTime } from "@/lib/format";
import type { AdminCustomer } from "@/types";

export function AdminCustomersTab() {
  const { data: customers, isLoading } = useAdminCustomers();
  const { block, unblock, resetPassword, deleteUser } = useAdminCustomerActions();
  const [deleteTarget, setDeleteTarget] = useState<AdminCustomer | null>(null);

  if (isLoading) return <PageSpinner />;

  if (!customers || customers.length === 0) {
    return (
      <p className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
        No customer accounts yet.
      </p>
    );
  }

  return (
    <div>
      <div className="space-y-2">
        {customers.map((customer) => (
          <Card key={customer.id}>
            <CardContent className="flex flex-wrap items-center justify-between gap-3 py-3 text-sm">
              <div className="min-w-0">
                <p className="font-medium">{customer.full_name}</p>
                <p className="text-xs text-muted-foreground">
                  {customer.email} &middot; {customer.phone}
                </p>
              </div>
              <div className="text-xs text-muted-foreground">
                <p>{customer.total_orders} orders</p>
                <p>{formatCurrency(customer.total_spend)} spent</p>
              </div>
              <p className="text-xs text-muted-foreground">
                {customer.last_order_at ? `Last order ${formatDateTime(customer.last_order_at)}` : "No orders yet"}
              </p>
              <Badge variant={customer.is_active ? "default" : "outline"}>
                {customer.is_active ? "Active" : "Blocked"}
              </Badge>
              <div className="flex flex-wrap gap-2">
                <Button
                  size="sm"
                  variant="outline"
                  disabled={block.isPending || unblock.isPending}
                  onClick={() =>
                    customer.is_active ? block.mutate(customer.id) : unblock.mutate(customer.id)
                  }
                >
                  {customer.is_active ? "Block" : "Unblock"}
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  disabled={resetPassword.isPending}
                  onClick={() => resetPassword.mutate(customer.id)}
                >
                  Reset password
                </Button>
                <Button size="sm" variant="destructive" onClick={() => setDeleteTarget(customer)}>
                  Delete
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <Dialog open={!!deleteTarget} onOpenChange={(open) => !open && setDeleteTarget(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete {deleteTarget?.full_name}&apos;s account?</DialogTitle>
          </DialogHeader>
          <p className="text-sm text-muted-foreground">
            This deactivates the account and removes their personal details. Their order history is kept
            (required for records) but is no longer linked to identifying information. This can&apos;t be undone.
          </p>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteTarget(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              disabled={deleteUser.isPending}
              onClick={() =>
                deleteTarget && deleteUser.mutate(deleteTarget.id, { onSuccess: () => setDeleteTarget(null) })
              }
            >
              {deleteUser.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Delete account
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
