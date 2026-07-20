import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { Bike, ClipboardList, Flame, Search, Sparkles, UtensilsCrossed } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { CategoryChips } from "@/components/food/CategoryChips";
import { FoodRow } from "@/components/food/FoodRow";
import { useCategories, useFoods } from "@/hooks/useMenu";

const STATS = [
  { value: "20+", label: "menu items" },
  { value: "4", label: "campus roles" },
  { value: "Live", label: "order tracking" },
];

const STEPS = [
  {
    number: "01",
    icon: Search,
    title: "Browse & order",
    text: "Search the canteen menu, filter by category or veg/non-veg, and add what you're craving to your cart.",
  },
  {
    number: "02",
    icon: ClipboardList,
    title: "Kitchen gets to work",
    text: "Your order lands in the kitchen queue the moment you pay — accepted, prepped, and marked ready in real time.",
  },
  {
    number: "03",
    icon: Bike,
    title: "Delivered to your door",
    text: "A delivery partner is matched automatically and brings it straight to your hostel or department.",
  },
];

/** Small, original decorative accents — not from any external source. */
function HeroShapes() {
  return (
    <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
      <svg className="absolute -left-8 top-10 h-24 w-24 text-primary/20 sm:left-4" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="46" stroke="currentColor" strokeWidth="6" />
      </svg>
      <svg className="absolute right-2 top-24 h-16 w-16 text-gold/40 sm:right-16" viewBox="0 0 100 100" fill="none">
        <circle cx="50" cy="50" r="46" stroke="currentColor" strokeWidth="8" />
      </svg>
      <div className="absolute left-1/4 top-4 h-3 w-3 rounded-full bg-primary/30" />
      <div className="absolute right-1/3 bottom-6 h-2 w-2 rounded-full bg-gold/50" />
      <div className="absolute left-10 bottom-10 h-4 w-4 rounded-full bg-success/20" />
    </div>
  );
}

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
        <HeroShapes />
        <div className="container relative flex flex-col items-center gap-6 py-16 text-center sm:py-24">
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
            <h1 className="max-w-2xl text-balance font-heading text-5xl font-bold tracking-tight sm:text-6xl">
              We don't just cook,{" "}
              <span className="text-primary">we deliver campus favourites.</span>
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

          <div className="mt-2 flex items-center gap-8 sm:gap-12">
            {STATS.map((stat) => (
              <div key={stat.label} className="flex flex-col items-center">
                <span className="font-heading text-2xl font-bold text-primary sm:text-3xl">{stat.value}</span>
                <span className="text-xs text-muted-foreground">{stat.label}</span>
              </div>
            ))}
          </div>
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

      <section className="container py-12">
        <h2 className="mb-8 text-center font-heading text-2xl font-bold">How it works</h2>
        <div className="grid gap-8 sm:grid-cols-3">
          {STEPS.map((step) => (
            <div key={step.number} className="relative rounded-2xl border border-border/60 p-6">
              <span className="font-heading text-4xl font-bold text-primary/15">{step.number}</span>
              <step.icon className="mt-2 h-6 w-6 text-primary" />
              <h3 className="mt-3 font-heading text-base font-semibold">{step.title}</h3>
              <p className="mt-1.5 text-sm text-muted-foreground">{step.text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container pb-16">
        <div className="relative overflow-hidden rounded-2xl bg-deep px-6 py-12 text-center text-deep-foreground">
          <div aria-hidden className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-gold/10" />
          <div aria-hidden className="pointer-events-none absolute -bottom-12 -left-8 h-32 w-32 rounded-full bg-primary/10" />
          <h2 className="relative font-heading text-2xl font-bold">Hungry for something specific?</h2>
          <p className="relative mx-auto mt-2 max-w-md text-sm text-deep-foreground/70">
            Browse the full menu — filter by category, price, rating, or veg/non-veg.
          </p>
          <Button className="relative mt-5 bg-gold text-gold-foreground hover:bg-gold/90" asChild>
            <a href="/menu">Browse full menu</a>
          </Button>
        </div>
      </section>
    </div>
  );
}
