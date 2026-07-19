import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import { ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { FoodCard } from "@/components/food/FoodCard";
import type { Food } from "@/types";

export function FoodRow({
  title,
  icon,
  foods,
  isLoading,
  seeAllHref,
}: {
  title: string;
  icon?: ReactNode;
  foods: Food[] | undefined;
  isLoading: boolean;
  seeAllHref?: string;
}) {
  if (!isLoading && (!foods || foods.length === 0)) return null;

  return (
    <section className="container py-8">
      <div className="mb-4 flex items-center justify-between">
        <h2 className="flex items-center gap-2 font-heading text-xl font-bold">
          {icon}
          {title}
        </h2>
        {seeAllHref && (
          <Button variant="ghost" size="sm" asChild>
            <Link to={seeAllHref}>
              See all <ArrowRight className="h-4 w-4" />
            </Link>
          </Button>
        )}
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {isLoading
          ? Array.from({ length: 5 }).map((_, i) => <Skeleton key={i} className="aspect-[4/5] rounded-xl" />)
          : foods!.map((food) => <FoodCard key={food.id} food={food} />)}
      </div>
    </section>
  );
}
