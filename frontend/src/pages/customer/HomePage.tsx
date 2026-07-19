import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Flame, Search, Sparkles, UtensilsCrossed } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CategoryChips } from "@/components/food/CategoryChips";
import { FoodRow } from "@/components/food/FoodRow";
import { useCategories, useFoods } from "@/hooks/useMenu";

export function HomePage() {
  const navigate = useNavigate();
  const [query, setQuery] = useState("");

  const { data: categories, isLoading: categoriesLoading } = useCategories();
  const { data: popularFoods, isLoading: popularLoading } = useFoods({ is_popular: true, limit: 10 });
  const { data: specialFoods, isLoading: specialsLoading } = useFoods({ is_special_today: true, limit: 10 });

  function handleSearch(event: FormEvent) {
    event.preventDefault();
    navigate(query.trim() ? `/menu?q=${encodeURIComponent(query.trim())}` : "/menu");
  }

  return (
    <div>
      <section className="relative overflow-hidden border-b border-border/60 bg-gradient-to-b from-accent/40 to-background">
        <div className="container flex flex-col items-center gap-6 py-16 text-center sm:py-24">
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center gap-4"
          >
            <span className="inline-flex items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary">
              <UtensilsCrossed className="h-3.5 w-3.5" />
              Delivered right to your hostel or department
            </span>
            <h1 className="max-w-2xl text-balance font-heading text-4xl font-bold tracking-tight sm:text-5xl">
              Campus food, ordered in seconds.
            </h1>
            <p className="max-w-lg text-balance text-muted-foreground">
              Idlis, dosas, juices, and full meals from the canteen — order online and track it live from kitchen
              to your door.
            </p>
          </motion.div>

          <form onSubmit={handleSearch} className="flex w-full max-w-lg items-center gap-2">
            <div className="relative flex-1">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for masala dosa, filter coffee, juices..."
                className="h-11 pl-9"
              />
            </div>
            <Button type="submit" size="lg" className="h-11">
              Search
            </Button>
          </form>
        </div>
      </section>

      <div className="container pt-8">
        <h2 className="mb-3 font-heading text-lg font-semibold">Shop by category</h2>
        <CategoryChips categories={categories} isLoading={categoriesLoading} />
      </div>

      <FoodRow
        title="Popular right now"
        icon={<Flame className="h-5 w-5 text-primary" />}
        foods={popularFoods}
        isLoading={popularLoading}
        seeAllHref="/menu?is_popular=true"
      />

      <FoodRow
        title="Today's specials"
        icon={<Sparkles className="h-5 w-5 text-primary" />}
        foods={specialFoods}
        isLoading={specialsLoading}
        seeAllHref="/menu?is_special_today=true"
      />

      <section className="container pb-16 pt-4">
        <div className="flex flex-col items-center gap-3 rounded-2xl border border-border/60 bg-muted/40 px-6 py-10 text-center">
          <h2 className="font-heading text-xl font-bold">Hungry for something specific?</h2>
          <p className="max-w-md text-sm text-muted-foreground">
            Browse the full menu — filter by category, price, rating, or veg/non-veg.
          </p>
          <Button asChild>
            <a href="/menu">Browse full menu</a>
          </Button>
        </div>
      </section>
    </div>
  );
}
