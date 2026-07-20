import { useState } from "react";
import { toast } from "sonner";
import { Bike, IndianRupee, Loader2, LocateFixed, MapPin, Package, Phone, Star } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Dialog, DialogContent, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { PageSpinner } from "@/components/PageSpinner";
import { DeliveryLiveMap } from "@/components/map/DeliveryLiveMap";
import { useDeliveryActions, useDeliveryOrders, useDeliveryProfile } from "@/hooks/useDelivery";
import { formatCurrency } from "@/lib/format";
import type { Order } from "@/types";

function DeliverDialog({ order, onClose }: { order: Order; onClose: () => void }) {
  const { deliver } = useDeliveryActions();
  const [otp, setOtp] = useState("");

  return (
    <Dialog open onOpenChange={(open) => !open && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Confirm delivery — {order.order_number}</DialogTitle>
        </DialogHeader>
        <div className="space-y-1.5">
          <Label htmlFor="otp">Ask the customer for their 6-digit OTP</Label>
          <Input
            id="otp"
            inputMode="numeric"
            maxLength={6}
            value={otp}
            onChange={(e) => setOtp(e.target.value.replace(/\D/g, ""))}
          />
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button
            disabled={otp.length !== 6 || deliver.isPending}
            onClick={() => deliver.mutate({ orderId: order.id, otp }, { onSuccess: onClose })}
          >
            {deliver.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
            Confirm delivered
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function DeliveryOrderCard({ order, onDeliver }: { order: Order; onDeliver: (order: Order) => void }) {
  const { pickup, onTheWay } = useDeliveryActions();
  const busy = pickup.isPending || onTheWay.isPending;

  return (
    <Card>
      <CardContent className="space-y-2 py-3 text-sm">
        <div className="flex items-start justify-between">
          <p className="font-medium">{order.order_number}</p>
          <Badge variant="secondary" className="capitalize">
            {order.status.replace(/_/g, " ")}
          </Badge>
        </div>
        <div className="flex items-center gap-1 text-xs text-muted-foreground">
          <MapPin className="h-3 w-3" />
          {[order.address.hostel, order.address.building, order.address.room_number && `Room ${order.address.room_number}`]
            .filter(Boolean)
            .join(", ") || "No address details"}
        </div>
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <span className="flex items-center gap-1">
            <Phone className="h-3 w-3" /> {order.customer_name}
          </span>
          <Button variant="ghost" size="icon-sm" asChild>
            <a href={`tel:${order.customer_phone}`}>
              <Phone className="h-3.5 w-3.5" />
            </a>
          </Button>
        </div>

        <div className="pt-1">
          {order.status === "assigned" && (
            <Button size="sm" className="w-full" disabled={busy} onClick={() => pickup.mutate(order.id)}>
              {pickup.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              Mark picked up
            </Button>
          )}
          {order.status === "picked_up" && (
            <Button size="sm" className="w-full" disabled={busy} onClick={() => onTheWay.mutate(order.id)}>
              {onTheWay.isPending && <Loader2 className="h-3.5 w-3.5 animate-spin" />}
              Start delivery
            </Button>
          )}
          {order.status === "on_the_way" && (
            <Button size="sm" className="w-full" onClick={() => onDeliver(order)}>
              Confirm delivery (OTP)
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export function DeliveryDashboardPage() {
  const { data: profile, isLoading: profileLoading, isError: profileMissing } = useDeliveryProfile();
  const { data: orders, isLoading: ordersLoading } = useDeliveryOrders();
  const { updateLocation } = useDeliveryActions();
  const [deliverTarget, setDeliverTarget] = useState<Order | null>(null);
  const [locating, setLocating] = useState(false);

  if (profileLoading || ordersLoading) return <PageSpinner />;

  if (profileMissing || !profile) {
    return (
      <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-2 text-center">
        <Bike className="h-10 w-10 text-muted-foreground" />
        <h1 className="font-heading text-xl font-bold">No delivery partner profile yet</h1>
        <p className="text-sm text-muted-foreground">Ask an admin to set up your delivery partner profile.</p>
      </div>
    );
  }

  function captureLocation() {
    if (!navigator.geolocation) {
      toast.error("Your browser doesn't support location detection");
      return;
    }
    setLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        updateLocation.mutate({ latitude: pos.coords.latitude, longitude: pos.coords.longitude });
        setLocating(false);
      },
      () => {
        toast.error("Could not detect your location");
        setLocating(false);
      },
      { enableHighAccuracy: true, timeout: 10_000 },
    );
  }

  return (
    <div className="container py-8">
      <h1 className="flex items-center gap-2 font-heading text-2xl font-bold">
        <Bike className="h-6 w-6 text-primary" /> Delivery dashboard
      </h1>

      <div className="mt-6 grid gap-4 sm:grid-cols-3">
        <Card>
          <CardContent className="flex items-center gap-3 py-4">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-accent">
              <IndianRupee className="h-5 w-5 text-accent-foreground" />
            </span>
            <div>
              <p className="text-xs text-muted-foreground">Today&apos;s earnings</p>
              <p className="font-heading text-lg font-bold">{formatCurrency(profile.today_earnings)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 py-4">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-accent">
              <Package className="h-5 w-5 text-accent-foreground" />
            </span>
            <div>
              <p className="text-xs text-muted-foreground">Completed deliveries</p>
              <p className="font-heading text-lg font-bold">{profile.total_deliveries}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="flex items-center gap-3 py-4">
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-accent">
              <Star className="h-5 w-5 text-accent-foreground" />
            </span>
            <div>
              <p className="text-xs text-muted-foreground">Rating</p>
              <p className="font-heading text-lg font-bold">{profile.rating_avg.toFixed(1)}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardContent className="flex flex-wrap items-center justify-between gap-3 py-4">
          <div className="flex items-center gap-2">
            <Switch
              checked={profile.is_available}
              onCheckedChange={(checked) => updateLocation.mutate({ is_available: checked })}
            />
            <span className="text-sm font-medium">{profile.is_available ? "Available for orders" : "Not available"}</span>
          </div>
          <Button variant="outline" size="sm" onClick={captureLocation} disabled={locating}>
            {locating ? <Loader2 className="h-4 w-4 animate-spin" /> : <LocateFixed className="h-4 w-4" />}
            Update my location
          </Button>
        </CardContent>
        <CardContent className="pt-0">
          <DeliveryLiveMap latitude={profile.current_latitude} longitude={profile.current_longitude} />
        </CardContent>
      </Card>

      <h2 className="mt-8 mb-3 font-heading text-lg font-semibold">
        My orders {orders && orders.length > 0 && <Badge variant="secondary">{orders.length}</Badge>}
      </h2>
      {(!orders || orders.length === 0) && (
        <p className="rounded-lg border border-dashed border-border p-6 text-center text-sm text-muted-foreground">
          No orders assigned right now.
        </p>
      )}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {orders?.map((order) => (
          <DeliveryOrderCard key={order.id} order={order} onDeliver={setDeliverTarget} />
        ))}
      </div>

      {deliverTarget && <DeliverDialog order={deliverTarget} onClose={() => setDeliverTarget(null)} />}
    </div>
  );
}
