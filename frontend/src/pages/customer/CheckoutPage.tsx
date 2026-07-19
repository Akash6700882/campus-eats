import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Loader2, MapPin, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { Textarea } from "@/components/ui/textarea";
import { PageSpinner } from "@/components/PageSpinner";
import { AddressForm } from "@/components/address/AddressForm";
import { useAddresses } from "@/hooks/useAddresses";
import { cartQueryKey, useCart } from "@/hooks/useCart";
import { ordersApi } from "@/api/orders";
import { apiErrorMessage } from "@/lib/api";
import { formatCurrency } from "@/lib/format";

export function CheckoutPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const couponCode = searchParams.get("coupon") ?? undefined;
  const queryClient = useQueryClient();

  const { data: addresses, isLoading: addressesLoading } = useAddresses();
  const { data: cart, isLoading: cartLoading } = useCart(couponCode);

  const [selectedAddressId, setSelectedAddressId] = useState<string | undefined>();
  const [showAddForm, setShowAddForm] = useState(false);
  const [notes, setNotes] = useState("");
  const [placing, setPlacing] = useState(false);

  const effectiveAddressId =
    selectedAddressId ?? addresses?.find((a) => a.is_default)?.id ?? addresses?.[0]?.id;

  async function handlePlaceOrder() {
    if (!effectiveAddressId) {
      toast.error("Select or add a delivery address first");
      return;
    }
    setPlacing(true);
    try {
      const order = await ordersApi.checkout({
        address_id: effectiveAddressId,
        coupon_code: couponCode,
        notes: notes || undefined,
      });
      await queryClient.invalidateQueries({ queryKey: cartQueryKey });
      toast.success("Order placed!");
      navigate(`/orders/${order.id}`);
    } catch (err) {
      toast.error(apiErrorMessage(err, "Could not place your order"));
    } finally {
      setPlacing(false);
    }
  }

  if (addressesLoading || cartLoading) return <PageSpinner />;

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
        <h1 className="font-heading text-xl font-bold">Your cart is empty</h1>
        <Button asChild>
          <Link to="/menu">Browse the menu</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <h1 className="font-heading text-2xl font-bold">Checkout</h1>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="space-y-4 lg:col-span-2">
          <div className="flex items-center justify-between">
            <h2 className="flex items-center gap-1.5 font-heading text-lg font-semibold">
              <MapPin className="h-5 w-5" /> Delivery address
            </h2>
            <Button variant="ghost" size="sm" onClick={() => setShowAddForm((s) => !s)}>
              <Plus className="h-4 w-4" /> {showAddForm ? "Cancel" : "Add new"}
            </Button>
          </div>

          {showAddForm && (
            <Card>
              <CardContent className="py-4">
                <AddressForm
                  onCreated={(address) => {
                    setSelectedAddressId(address.id);
                    setShowAddForm(false);
                  }}
                />
              </CardContent>
            </Card>
          )}

          {!showAddForm && (!addresses || addresses.length === 0) && (
            <p className="text-sm text-muted-foreground">No saved addresses yet — add one to continue.</p>
          )}

          {!showAddForm && addresses && addresses.length > 0 && (
            <div className="space-y-2">
              {addresses.map((address) => (
                <label
                  key={address.id}
                  className={`flex cursor-pointer items-start gap-3 rounded-xl border p-3 transition-colors ${
                    effectiveAddressId === address.id ? "border-primary bg-accent/50" : "border-border"
                  }`}
                >
                  <input
                    type="radio"
                    name="address"
                    className="mt-1"
                    checked={effectiveAddressId === address.id}
                    onChange={() => setSelectedAddressId(address.id)}
                  />
                  <div className="text-sm">
                    <p className="font-medium">
                      {address.label}
                      {address.is_default && <span className="ml-2 text-xs text-muted-foreground">(default)</span>}
                    </p>
                    <p className="text-muted-foreground">
                      {[
                        address.hostel,
                        address.building,
                        address.block && `Block ${address.block}`,
                        address.room_number && `Room ${address.room_number}`,
                        address.department,
                      ]
                        .filter(Boolean)
                        .join(", ") || "No extra details"}
                    </p>
                  </div>
                </label>
              ))}
            </div>
          )}

          <div className="space-y-1.5 pt-2">
            <Label htmlFor="notes">Order notes (optional)</Label>
            <Textarea
              id="notes"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any special instructions for the kitchen..."
            />
          </div>
        </div>

        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-2 py-4 text-sm">
              <p className="mb-1 font-heading font-semibold">Order summary</p>
              {cart.items.map((item) => (
                <div key={item.id} className="flex justify-between text-muted-foreground">
                  <span>
                    {item.quantity} &times; {item.food_name}
                  </span>
                  <span>{formatCurrency(item.subtotal)}</span>
                </div>
              ))}
              <Separator className="my-1" />
              <div className="flex justify-between">
                <span className="text-muted-foreground">Item total</span>
                <span>{formatCurrency(cart.item_total)}</span>
              </div>
              {cart.discount_amount > 0 && (
                <div className="flex justify-between text-success">
                  <span>Discount</span>
                  <span>-{formatCurrency(cart.discount_amount)}</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-muted-foreground">Delivery</span>
                <span>{formatCurrency(cart.delivery_charge)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Packing</span>
                <span>{formatCurrency(cart.packing_charge)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">GST</span>
                <span>{formatCurrency(cart.gst_amount)}</span>
              </div>
              <Separator className="my-1" />
              <div className="flex justify-between font-heading text-base font-bold">
                <span>Grand total</span>
                <span>{formatCurrency(cart.grand_total)}</span>
              </div>
            </CardContent>
          </Card>

          <Button className="w-full" size="lg" onClick={handlePlaceOrder} disabled={placing || !effectiveAddressId}>
            {placing && <Loader2 className="h-4 w-4 animate-spin" />}
            Place order
          </Button>
        </div>
      </div>
    </div>
  );
}
