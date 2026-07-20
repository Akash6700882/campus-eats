import { useState } from "react";
import { Clock, Heart, Minus, Plus, Star, UtensilsCrossed } from "lucide-react";
import { toast } from "sonner";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter } from "@/components/ui/card";
import { VegBadge } from "@/components/food/VegBadge";
import { ReviewsDialog } from "@/components/food/ReviewsDialog";
import { useCartMutations } from "@/hooks/useCart";
import { useWishlist, useWishlistMutations } from "@/hooks/useWishlist";
import { useAuth } from "@/store/auth";
import { cn } from "@/lib/utils";
import { formatCurrency } from "@/lib/format";
import type { Food } from "@/types";

export function FoodCard({ food }: { food: Food }) {
  const [quantity, setQuantity] = useState(1);
  const { addItem } = useCartMutations();
  const { isAuthenticated } = useAuth();
  const { data: wishlist } = useWishlist();
  const { add, remove } = useWishlistMutations();

  const hasDiscount = food.discount_percent > 0;
  const wishlistItem = wishlist?.find((w) => w.food.id === food.id);

  function toggleWishlist() {
    if (!isAuthenticated) {
      toast.error("Sign in to save favourites");
      return;
    }
    if (wishlistItem) remove.mutate(food.id);
    else add.mutate(food.id);
  }

  return (
    <Card className="group flex h-full flex-col transition-all duration-200 hover:-translate-y-0.5 hover:shadow-lg">
      <div className="relative aspect-[4/3] w-full overflow-hidden bg-muted">
        {food.image_url ? (
          <img
            src={food.image_url}
            alt={food.name}
            className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
            loading="lazy"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center text-muted-foreground">
            <UtensilsCrossed className="h-10 w-10" />
          </div>
        )}
        <div className="absolute left-2 top-2 flex flex-wrap gap-1">
          {food.is_special_today && <Badge className="bg-primary text-primary-foreground">Today&apos;s Special</Badge>}
          {food.is_popular && <Badge className="bg-gold text-gold-foreground">Popular</Badge>}
        </div>
        <div className="absolute right-2 top-2 flex flex-col items-end gap-1">
          <button
            type="button"
            onClick={toggleWishlist}
            aria-label={wishlistItem ? "Remove from wishlist" : "Add to wishlist"}
            className="flex h-7 w-7 items-center justify-center rounded-full bg-background/90 shadow-sm transition-colors hover:bg-background"
          >
            <Heart className={cn("h-3.5 w-3.5", wishlistItem ? "fill-destructive text-destructive" : "text-muted-foreground")} />
          </button>
          {hasDiscount && (
            <Badge className="bg-success text-success-foreground">{food.discount_percent}% off</Badge>
          )}
        </div>
        {!food.is_available && (
          <div className="absolute inset-0 flex items-center justify-center bg-background/80">
            <Badge variant="outline">Currently unavailable</Badge>
          </div>
        )}
      </div>

      <CardContent className="flex flex-1 flex-col gap-1.5 pt-3">
        <div className="flex items-start justify-between gap-2">
          <div className="flex items-center gap-1.5">
            <VegBadge isVeg={food.is_veg} />
            <h3 className="font-heading text-sm font-semibold leading-tight">{food.name}</h3>
          </div>
          <ReviewsDialog food={food}>
            <button type="button" className="flex shrink-0 items-center gap-0.5 text-xs font-medium text-muted-foreground hover:text-foreground">
              <Star className="h-3 w-3 fill-primary text-primary" />
              {food.rating_count > 0 ? food.rating_avg.toFixed(1) : "New"}
            </button>
          </ReviewsDialog>
        </div>

        {food.description && <p className="line-clamp-2 text-xs text-muted-foreground">{food.description}</p>}

        <div className="mt-auto flex items-center justify-between pt-1">
          <div className="flex items-baseline gap-1.5">
            <span className="font-heading text-sm font-bold">{formatCurrency(food.discounted_price)}</span>
            {hasDiscount && (
              <span className="text-xs text-muted-foreground line-through">{formatCurrency(food.price)}</span>
            )}
          </div>
          <span className="flex items-center gap-0.5 text-xs text-muted-foreground">
            <Clock className="h-3 w-3" />
            {food.prep_time_minutes}m
          </span>
        </div>
      </CardContent>

      <CardFooter className="gap-2 bg-transparent p-3 pt-0">
        <div className="flex items-center rounded-lg border border-input">
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label="Decrease quantity"
            disabled={quantity <= 1}
            onClick={() => setQuantity((q) => Math.max(1, q - 1))}
          >
            <Minus className="h-3.5 w-3.5" />
          </Button>
          <span className="w-6 text-center text-sm font-medium">{quantity}</span>
          <Button
            type="button"
            variant="ghost"
            size="icon-sm"
            aria-label="Increase quantity"
            onClick={() => setQuantity((q) => Math.min(20, q + 1))}
          >
            <Plus className="h-3.5 w-3.5" />
          </Button>
        </div>
        <Button
          type="button"
          className="flex-1"
          size="sm"
          disabled={!food.is_available || addItem.isPending}
          onClick={() => addItem.mutate({ foodId: food.id, quantity })}
        >
          Add to cart
        </Button>
      </CardFooter>
    </Card>
  );
}
