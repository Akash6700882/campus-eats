import { Link } from "react-router-dom";
import { Heart } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PageSpinner } from "@/components/PageSpinner";
import { FoodCard } from "@/components/food/FoodCard";
import { useWishlist } from "@/hooks/useWishlist";

export function WishlistPage() {
  const { data: wishlist, isLoading } = useWishlist();

  if (isLoading) return <PageSpinner />;

  if (!wishlist || wishlist.length === 0) {
    return (
      <div className="container flex min-h-[60vh] flex-col items-center justify-center gap-4 text-center">
        <Heart className="h-10 w-10 text-muted-foreground" />
        <h1 className="font-heading text-xl font-bold">Your wishlist is empty</h1>
        <p className="text-sm text-muted-foreground">Tap the heart on any food card to save it here.</p>
        <Button asChild>
          <Link to="/menu">Browse the menu</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="container py-8">
      <h1 className="flex items-center gap-2 font-heading text-2xl font-bold">
        <Heart className="h-6 w-6 fill-destructive text-destructive" /> My wishlist
      </h1>
      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {wishlist.map((item) => (
          <FoodCard key={item.id} food={item.food} />
        ))}
      </div>
    </div>
  );
}
