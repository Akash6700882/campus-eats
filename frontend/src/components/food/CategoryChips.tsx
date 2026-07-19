import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import { Skeleton } from "@/components/ui/skeleton";
import type { Category } from "@/types";

export function CategoryChips({
  categories,
  isLoading,
  activeCategoryId,
}: {
  categories: Category[] | undefined;
  isLoading: boolean;
  activeCategoryId?: string;
}) {
  if (isLoading) {
    return (
      <div className="flex gap-2 overflow-x-auto pb-1">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-9 w-24 shrink-0 rounded-full" />
        ))}
      </div>
    );
  }

  return (
    <div className="flex gap-2 overflow-x-auto pb-1">
      <Link
        to="/menu"
        className={cn(
          "shrink-0 rounded-full border border-input px-4 py-2 text-sm font-medium transition-colors hover:bg-accent",
          !activeCategoryId && "border-primary bg-primary text-primary-foreground hover:bg-primary/90",
        )}
      >
        All
      </Link>
      {categories?.map((category) => (
        <Link
          key={category.id}
          to={`/menu?category_id=${category.id}`}
          className={cn(
            "shrink-0 rounded-full border border-input px-4 py-2 text-sm font-medium transition-colors hover:bg-accent",
            activeCategoryId === category.id && "border-primary bg-primary text-primary-foreground hover:bg-primary/90",
          )}
        >
          {category.name}
        </Link>
      ))}
    </div>
  );
}
