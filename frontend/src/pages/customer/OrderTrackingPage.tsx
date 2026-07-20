import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Bike, Copy, Download, KeyRound, Loader2, Phone, ReceiptText } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { PageSpinner } from "@/components/PageSpinner";
import { StatusTimeline } from "@/components/order/StatusTimeline";
import { RateOrderItem } from "@/components/order/RateOrderItem";
import { useOrder, useCancelOrder } from "@/hooks/useOrders";
import { useOrderSocket } from "@/hooks/useOrderSocket";
import { cartQueryKey } from "@/hooks/useCart";
import { paymentsApi } from "@/api/payments";
import { apiErrorMessage } from "@/lib/api";
import { formatCurrency, formatDateTime } from "@/lib/format";
import { loadRazorpayScript } from "@/lib/razorpay";

const CUSTOMER_CANCELLABLE = new Set(["pending", "accepted", "preparing"]);

export function OrderTrackingPage() {
  const { id } = useParams<{ id: string }>();
  const { data: order, isLoading } = useOrder(id);
  const cancelOrder = useCancelOrder(id ?? "");
  const queryClient = useQueryClient();
  const [paying, setPaying] = useState(false);

  useOrderSocket(order?.status === "delivered" || order?.status === "cancelled" ? undefined : id);

  async function handlePay() {
    if (!order) return;
    setPaying(true);
    try {
      const initiate = await paymentsApi.initiate(order.id);
      await loadRazorpayScript();
      if (!window.Razorpay) throw new Error("Razorpay checkout script did not load");

      const rzp = new window.Razorpay({
        key: initiate.razorpay_key_id,
        amount: Math.round(initiate.amount * 100),
        currency: initiate.currency,
        order_id: initiate.razorpay_order_id,
        name: "Campus Eats",
        description: `Order ${order.order_number}`,
        prefill: { name: order.customer_name, contact: order.customer_phone },
        theme: { color: "#ea580c" },
        handler: (response) => {
          paymentsApi
            .verify(order.id, response)
            .then(() => {
              toast.success("Payment successful!");
              queryClient.invalidateQueries({ queryKey: ["orders", order.id] });
            })
            .catch((err) => toast.error(apiErrorMessage(err, "Payment verification failed — please retry")));
        },
        modal: { ondismiss: () => setPaying(false) },
      });
      rzp.open();
      setPaying(false);
    } catch (err) {
      toast.error(apiErrorMessage(err, "Could not start payment — Razorpay may not be configured yet"));
      setPaying(false);
    }
  }

  async function handleCancelUnpaid() {
    if (!order) return;
    try {
      await paymentsApi.cancel(order.id);
      toast.success("Order cancelled — items restored to your cart");
      queryClient.invalidateQueries({ queryKey: ["orders", order.id] });
      queryClient.invalidateQueries({ queryKey: cartQueryKey });
    } catch (err) {
      toast.error(apiErrorMessage(err, "Could not cancel order"));
    }
  }

  function copyOtp() {
    if (!order?.delivery_otp) return;
    navigator.clipboard.writeText(order.delivery_otp);
    toast.success("OTP copied");
  }

  if (isLoading) return <PageSpinner />;
  if (!order) {
    return (
      <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
        <h1 className="font-heading text-xl font-bold">Order not found</h1>
        <Button asChild>
          <Link to="/orders">Back to my orders</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <div className="mb-6 flex flex-wrap items-center justify-between gap-2">
        <div>
          <h1 className="font-heading text-2xl font-bold">Order {order.order_number}</h1>
          <p className="text-sm text-muted-foreground">Placed {order.placed_at ? formatDateTime(order.placed_at) : formatDateTime(order.created_at)}</p>
        </div>
        <Button variant="outline" size="sm" onClick={() => paymentsApi.downloadInvoice(order.id, order.order_number)}>
          <Download className="h-4 w-4" /> Invoice
        </Button>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          {order.status === "pending" && (
            <Card className="border-primary/40">
              <CardContent className="flex flex-col gap-3 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-heading font-semibold">Payment pending</p>
                    <p className="text-sm text-muted-foreground">Complete payment so the kitchen can start preparing.</p>
                  </div>
                  <p className="font-heading text-xl font-bold">{formatCurrency(order.grand_total)}</p>
                </div>
                <div className="flex gap-2">
                  <Button className="flex-1" onClick={handlePay} disabled={paying}>
                    {paying && <Loader2 className="h-4 w-4 animate-spin" />}
                    Pay now
                  </Button>
                  <Button variant="outline" onClick={handleCancelUnpaid}>
                    Cancel order
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          <Card>
            <CardContent className="py-5">
              <StatusTimeline status={order.status} />
            </CardContent>
          </Card>

          {order.delivery_otp && order.status !== "delivered" && order.status !== "cancelled" && (
            <Card className="border-primary/40 bg-primary/5">
              <CardContent className="flex items-center justify-between py-4">
                <div className="flex items-center gap-2">
                  <KeyRound className="h-5 w-5 text-primary" />
                  <div>
                    <p className="text-sm font-medium">Delivery OTP</p>
                    <p className="text-xs text-muted-foreground">Share this with the delivery partner on handoff</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <span className="font-heading text-2xl font-bold tracking-widest">{order.delivery_otp}</span>
                  <Button variant="ghost" size="icon-sm" onClick={copyOtp}>
                    <Copy className="h-4 w-4" />
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}

          {order.delivery_partner && (
            <Card>
              <CardContent className="flex items-center justify-between py-4">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 items-center justify-center rounded-full bg-accent">
                    <Bike className="h-5 w-5 text-accent-foreground" />
                  </span>
                  <div>
                    <p className="text-sm font-medium">{order.delivery_partner.full_name}</p>
                    <p className="text-xs text-muted-foreground">
                      {order.delivery_partner.vehicle_number ?? "Delivery partner"}
                    </p>
                  </div>
                </div>
                <Button variant="outline" size="sm" asChild>
                  <a href={`tel:${order.delivery_partner.phone}`}>
                    <Phone className="h-4 w-4" /> Call
                  </a>
                </Button>
              </CardContent>
            </Card>
          )}

          {order.status === "delivered" && (
            <Card>
              <CardContent className="space-y-3 py-4">
                <p className="font-heading font-semibold">Rate your order</p>
                {order.items.map((item) => (
                  <RateOrderItem key={item.food_id} orderId={order.id} item={item} />
                ))}
              </CardContent>
            </Card>
          )}

          {CUSTOMER_CANCELLABLE.has(order.status) && order.status !== "pending" && (
            <Button variant="outline" onClick={() => cancelOrder.mutate()} disabled={cancelOrder.isPending}>
              {cancelOrder.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
              Cancel order
            </Button>
          )}
        </div>

        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-2 py-4 text-sm">
              <p className="mb-1 flex items-center gap-1.5 font-heading font-semibold">
                <ReceiptText className="h-4 w-4" /> Order summary
              </p>
              {order.items.map((item) => (
                <div key={item.food_id} className="flex justify-between text-muted-foreground">
                  <span>
                    {item.quantity} &times; {item.food_name}
                  </span>
                  <span>{formatCurrency(item.subtotal)}</span>
                </div>
              ))}
              <Separator className="my-1" />
              <div className="flex justify-between">
                <span className="text-muted-foreground">Item total</span>
                <span>{formatCurrency(order.item_total)}</span>
              </div>
              {order.discount_amount > 0 && (
                <div className="flex justify-between text-success">
                  <span>Discount</span>
                  <span>-{formatCurrency(order.discount_amount)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-muted-foreground">Delivery</span>
                <span>{formatCurrency(order.delivery_charge)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Packing</span>
                <span>{formatCurrency(order.packing_charge)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">GST</span>
                <span>{formatCurrency(order.gst_amount)}</span>
              </div>
              <Separator className="my-1" />
              <div className="flex justify-between font-heading text-base font-bold">
                <span>Grand total</span>
                <span>{formatCurrency(order.grand_total)}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="space-y-1 py-4 text-sm">
              <p className="mb-1 font-heading font-semibold">Delivering to</p>
              <p className="font-medium">{order.address.label}</p>
              <p className="text-muted-foreground">
                {[order.address.hostel, order.address.building, order.address.block && `Block ${order.address.block}`, order.address.room_number && `Room ${order.address.room_number}`]
                  .filter(Boolean)
                  .join(", ") || "No extra details"}
              </p>
              {order.notes && <p className="pt-1 text-xs text-muted-foreground">Note: {order.notes}</p>}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
