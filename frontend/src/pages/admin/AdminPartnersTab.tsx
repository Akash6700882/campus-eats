import { useState } from "react";
import { Loader2, Plus, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { PageSpinner } from "@/components/PageSpinner";
import { useAdminDeliveryPartners, useCreateDeliveryPartner, useDeliveryRoleUsers } from "@/hooks/useAdmin";
import { formatCurrency } from "@/lib/format";

export function AdminPartnersTab() {
  const { data: partners, isLoading } = useAdminDeliveryPartners();
  const [open, setOpen] = useState(false);
  const { data: deliveryUsers, isLoading: usersLoading } = useDeliveryRoleUsers(open);
  const createPartner = useCreateDeliveryPartner();

  const [userId, setUserId] = useState("");
  const [vehicleNumber, setVehicleNumber] = useState("");

  const existingPartnerUserIds = new Set(partners?.map((p) => p.user_id));
  const eligibleUsers = deliveryUsers?.filter((u) => !existingPartnerUserIds.has(u.id)) ?? [];

  function handleCreate() {
    if (!userId) return;
    createPartner.mutate(
      { user_id: userId, vehicle_number: vehicleNumber || undefined },
      {
        onSuccess: () => {
          setOpen(false);
          setUserId("");
          setVehicleNumber("");
        },
      },
    );
  }

  return (
    <div>
      <div className="mb-4 flex justify-end">
        <Button size="sm" onClick={() => setOpen(true)}>
          <Plus className="h-4 w-4" /> Add delivery partner
        </Button>
      </div>

      {isLoading ? (
        <PageSpinner />
      ) : !partners || partners.length === 0 ? (
        <p className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
          No delivery partners yet.
        </p>
      ) : (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {partners.map((partner) => (
            <Card key={partner.id}>
              <CardContent className="space-y-1.5 py-4 text-sm">
                <div className="flex items-start justify-between">
                  <p className="font-medium">{partner.full_name}</p>
                  <Badge variant={partner.is_available ? "default" : "outline"}>
                    {partner.is_available ? "Available" : "Offline"}
                  </Badge>
                </div>
                <p className="text-muted-foreground">{partner.phone}</p>
                <p className="text-muted-foreground">{partner.vehicle_number ?? "No vehicle on file"}</p>
                <div className="flex items-center justify-between pt-1 text-xs text-muted-foreground">
                  <span className="flex items-center gap-1">
                    <Star className="h-3 w-3 fill-primary text-primary" /> {partner.rating_avg.toFixed(1)}
                  </span>
                  <span>{partner.total_deliveries} deliveries</span>
                  <span>{formatCurrency(partner.today_earnings)} today</span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add a delivery partner</DialogTitle>
          </DialogHeader>
          <div className="space-y-3">
            <div className="space-y-1.5">
              <Label>Delivery-role user</Label>
              <Select value={userId} onValueChange={setUserId}>
                <SelectTrigger>
                  <SelectValue placeholder={usersLoading ? "Loading..." : "Select a user"} />
                </SelectTrigger>
                <SelectContent>
                  {eligibleUsers.length === 0 && !usersLoading ? (
                    <p className="px-2 py-1.5 text-sm text-muted-foreground">
                      No delivery-role users without a profile
                    </p>
                  ) : (
                    eligibleUsers.map((u) => (
                      <SelectItem key={u.id} value={u.id}>
                        {u.full_name} ({u.phone})
                      </SelectItem>
                    ))
                  )}
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label htmlFor="vehicle">Vehicle number (optional)</Label>
              <Input id="vehicle" value={vehicleNumber} onChange={(e) => setVehicleNumber(e.target.value)} />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>
              Cancel
            </Button>
            <Button disabled={!userId || createPartner.isPending} onClick={handleCreate}>
              {createPartner.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Create profile
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
