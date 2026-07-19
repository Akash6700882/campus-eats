import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Loader2, Minus, Plus, ShoppingBag, Tag, Trash2, UtensilsCrossed } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { PageSpinner } from "@/components/PageSpinner";
import { useCart, useCartMutations } from "@/hooks/useCart";
import { formatCurrency } from "@/lib/format";
import { useAuth } from "@/store/auth";

export function CartPage() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [couponInput, setCouponInput] = useState("");
  const [appliedCoupon, setAppliedCoupon] = useState<string | undefined>(undefined);

  const { data: cart, isLoading } = useCart(appliedCoupon);
  const { updateQuantity, removeItem } = useCartMutations();

  if (!isAuthenticated) {
    return (
      <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
        <ShoppingBag className="h-10 w-10 text-muted-foreground" />
        <h1 className="font-heading text-xl font-bold">Sign in to see your cart</h1>
        <Button asChild>
          <Link to="/login">Sign in</Link>
        </Button>
      </div>
    );
  }

  if (isLoading) return <PageSpinner />;

  if (!cart || cart.items.length === 0) {
    return (
      <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
        <ShoppingBag className="h-10 w-10 text-muted-foreground" />
        <h1 className="font-heading text-xl font-bold">Your cart is empty</h1>
        <p className="text-sm text-muted-foreground">Add something tasty from the menu to get started.</p>
        <Button asChild>
          <Link to="/menu">Browse the menu</Link>
        </Button>
      </div>
    );
  }

  function handleApplyCoupon() {
    setAppliedCoupon(couponInput.trim() ? couponInput.trim().toUpperCase() : undefined);
  }

  function handleCheckout() {
    const params = appliedCoupon ? `?coupon=${encodeURIComponent(appliedCoupon)}` : "";
    navigate(`/checkout${params}`);
  }

  return (
    <div className="container py-8">
      <h1 className="font-heading text-2xl font-bold">Your cart</h1>

      <div className="mt-6 grid gap-6 lg:grid-cols-3">
        <div className="space-y-3 lg:col-span-2">
          {cart.items.map((item) => (
            <Card key={item.id}>
              <CardContent className="flex items-center gap-3 py-3">
                <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-lg bg-muted">
                  {item.image_url ? (
                    <img src={item.image_url} alt={item.food_name} className="h-full w-full rounded-lg object-cover" />
                  ) : (
                    <UtensilsCrossed className="h-6 w-6 text-muted-foreground" />
                  )}
                </div>

                <div className="min-w-0 flex-1">
                  <p className="truncate font-medium">{item.food_name}</p>
                  {!item.is_available && <p className="text-xs text-destructive">No longer available</p>}
                  <p className="text-sm text-muted-foreground">{formatCurrency(item.unit_price)} each</p>
                </div>

                <div className="flex items-center rounded-lg border border-input">
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    disabled={updateQuantity.isPending}
                    onClick={() =>
                      item.quantity > 1
                        ? updateQuantity.mutate({ foodId: item.food_id, quantity: item.quantity - 1 })
                        : removeItem.mutate(item.food_id)
                    }
                  >
                    <Minus className="h-3.5 w-3.5" />
                  </Button>
                  <span className="w-6 text-center text-sm font-medium">{item.quantity}</span>
                  <Button
                    variant="ghost"
                    size="icon-sm"
                    disabled={updateQuantity.isPending}
                    onClick={() => updateQuantity.mutate({ foodId: item.food_id, quantity: item.quantity + 1 })}
                  >
                    <Plus className="h-3.5 w-3.5" />
                  </Button>
                </div>

                <p className="w-20 shrink-0 text-right font-semibold">{formatCurrency(item.subtotal)}</p>

                <Button
                  variant="ghost"
                  size="icon-sm"
                  className="text-muted-foreground hover:text-destructive"
                  onClick={() => removeItem.mutate(item.food_id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        <div className="space-y-4">
          <Card>
            <CardContent className="space-y-3 py-4">
              <p className="flex items-center gap-1.5 text-sm font-medium">
                <Tag className="h-4 w-4" /> Coupon code
              </p>
              <div className="flex gap-2">
                <Input
                  value={couponInput}
                  onChange={(e) => setCouponInput(e.target.value)}
                  placeholder="e.g. WELCOME50"
                  className="uppercase"
                />
                <Button variant="secondary" onClick={handleApplyCoupon} disabled={isLoading}>
                  Apply
                </Button>
              </div>
              {cart.coupon_error && <p className="text-xs text-destructive">{cart.coupon_error}</p>}
              {cart.coupon_code && !cart.coupon_error && (
                <p className="text-xs text-success">Coupon &quot;{cart.coupon_code}&quot; applied</p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent className="space-y-2 py-4 text-sm">
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
                <span className="text-muted-foreground">Delivery charge</span>
                <span>{formatCurrency(cart.delivery_charge)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Packing charge</span>
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
              <p className="text-xs text-muted-foreground">
                Estimated delivery: ~{cart.estimated_delivery_minutes} minutes
              </p>
            </CardContent>
          </Card>

          <Button className="w-full" size="lg" onClick={handleCheckout} disabled={cart.items.some((i) => !i.is_available)}>
            {isLoading && <Loader2 className="h-4 w-4 animate-spin" />}
            Proceed to checkout
          </Button>
        </div>
      </div>
    </div>
  );
}
