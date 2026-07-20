import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Search, SlidersHorizontal, X } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Skeleton } from "@/components/ui/skeleton";
import { CategoryChips } from "@/components/food/CategoryChips";
import { FoodCard } from "@/components/food/FoodCard";
import { useCategories, useFoods } from "@/hooks/useMenu";

const VEG_OPTIONS = [
  { value: "all", label: "All" },
  { value: "veg", label: "Veg only" },
  { value: "nonveg", label: "Non-veg only" },
];

const RATING_OPTIONS = [
  { value: "any", label: "Any rating" },
  { value: "4", label: "4+ stars" },
  { value: "3", label: "3+ stars" },
];

export function MenuPage() {
  const [searchParams, setSearchParams] = useSearchParams();

  const categoryId = searchParams.get("category_id") ?? undefined;
  const vegParam = searchParams.get("is_veg");
  const isPopular = searchParams.get("is_popular") === "true" ? true : undefined;
  const isSpecialToday = searchParams.get("is_special_today") === "true" ? true : undefined;
  const minRating = searchParams.get("min_rating");
  const q = searchParams.get("q") ?? undefined;

  const [queryInput, setQueryInput] = useState(q ?? "");
  const [prevQ, setPrevQ] = useState(q);
  if (q !== prevQ) {
    setPrevQ(q);
    setQueryInput(q ?? "");
  }

  useEffect(() => {
    const handle = setTimeout(() => {
      if (queryInput === (q ?? "")) return;
      updateParam("q", queryInput || undefined);
    }, 400);
    return () => clearTimeout(handle);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [queryInput]);

  const { data: categories, isLoading: categoriesLoading } = useCategories();
  const { data: foods, isLoading } = useFoods({
    q,
    category_id: categoryId,
    is_veg: vegParam === "veg" ? true : vegParam === "nonveg" ? false : undefined,
    is_popular: isPopular,
    is_special_today: isSpecialToday,
    min_rating: minRating ? Number(minRating) : undefined,
    limit: 100,
  });

  function updateParam(key: string, value: string | undefined) {
    const next = new URLSearchParams(searchParams);
    if (!value || value === "all" || value === "any") next.delete(key);
    else next.set(key, value);
    setSearchParams(next, { replace: true });
  }

  const activeFilterChips: { key: string; label: string }[] = [];
  if (isPopular) activeFilterChips.push({ key: "is_popular", label: "Popular" });
  if (isSpecialToday) activeFilterChips.push({ key: "is_special_today", label: "Today's special" });

  return (
    <div className="container py-8">
      <h1 className="font-heading text-2xl font-bold">Full menu</h1>
      <p className="mt-1 text-sm text-muted-foreground">Search and filter everything the canteen has to offer.</p>

      <div className="mt-6 flex flex-col gap-4">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="Search food by name..."
            className="h-10 pl-9"
          />
        </div>

        <CategoryChips categories={categories} isLoading={categoriesLoading} activeCategoryId={categoryId} />

        <div className="flex flex-wrap items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-muted-foreground" />
          <Select value={vegParam ?? "all"} onValueChange={(v) => updateParam("is_veg", v)}>
            <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
            <SelectContent>
              {VEG_OPTIONS.map((o) => (
                <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          <Select value={minRating ?? "any"} onValueChange={(v) => updateParam("min_rating", v)}>
            <SelectTrigger className="w-36"><SelectValue /></SelectTrigger>
            <SelectContent>
              {RATING_OPTIONS.map((o) => (
                <SelectItem key={o.value} value={o.value}>{o.label}</SelectItem>
              ))}
            </SelectContent>
          </Select>

          {activeFilterChips.map((chip) => (
            <Badge key={chip.key} variant="secondary" className="gap-1 pr-1">
              {chip.label}
              <button
                type="button"
                className="rounded-full p-0.5 hover:bg-foreground/10"
                onClick={() => updateParam(chip.key, undefined)}
              >
                <X className="h-3 w-3" />
              </button>
            </Badge>
          ))}
        </div>
      </div>

      <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
        {isLoading &&
          Array.from({ length: 10 }).map((_, i) => <Skeleton key={i} className="aspect-[4/5] rounded-xl" />)}
        {!isLoading && foods?.length === 0 && (
          <p className="col-span-full py-16 text-center text-muted-foreground">
            No dishes match your filters — try clearing a few.
          </p>
        )}
        {!isLoading && foods?.map((food) => <FoodCard key={food.id} food={food} />)}
      </div>
    </div>
  );
}
