import { UtensilsCrossed } from "lucide-react";

export function Footer() {
  return (
    <footer className="mt-16 border-t border-border/60 bg-muted/30">
      <div className="container flex flex-col items-center justify-between gap-4 py-8 text-sm text-muted-foreground sm:flex-row">
        <div className="flex items-center gap-2 font-heading font-semibold text-foreground">
          <UtensilsCrossed className="h-4 w-4 text-primary" />
          Campus Eats
        </div>
        <p>Delivering across campus, one order at a time.</p>
        <p>&copy; {new Date().getFullYear()} Campus Eats</p>
      </div>
    </footer>
  );
}
