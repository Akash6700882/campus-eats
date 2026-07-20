import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Heart, LayoutDashboard, Menu, Moon, Search, ShoppingCart, Sun, UtensilsCrossed } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { NotificationsBell } from "@/components/layout/NotificationsBell";
import { useAuth } from "@/store/auth";
import { useTheme } from "@/store/theme";
import { useCart } from "@/hooks/useCart";

const NAV_LINKS = [
  { to: "/", label: "Home" },
  { to: "/menu", label: "Menu" },
  { to: "/orders", label: "My Orders" },
];

const STAFF_DASHBOARD_PATH: Record<string, string> = {
  admin: "/admin",
  kitchen: "/kitchen",
  delivery: "/delivery",
};

export function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const isStaff = !!user && user.role !== "customer";
  const { data: cart } = useCart();
  const navigate = useNavigate();
  const [query, setQuery] = useState("");
  const [mobileOpen, setMobileOpen] = useState(false);

  const itemCount = cart?.items.reduce((sum, item) => sum + item.quantity, 0) ?? 0;

  function handleSearch(event: FormEvent) {
    event.preventDefault();
    navigate(query.trim() ? `/menu?q=${encodeURIComponent(query.trim())}` : "/menu");
    setMobileOpen(false);
  }

  const logoHref = isStaff ? STAFF_DASHBOARD_PATH[user.role] : "/";

  return (
    <header className="sticky top-0 z-40 border-b border-border/60 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <div className="container flex h-16 items-center gap-4">
        <Link to={logoHref} className="flex shrink-0 items-center gap-2 font-heading text-lg font-bold">
          <UtensilsCrossed className="h-6 w-6 text-primary" />
          <span className="hidden sm:inline">Campus Eats</span>
          {isStaff && (
            <Badge variant="secondary" className="ml-1 capitalize">
              {user.role}
            </Badge>
          )}
        </Link>

        {!isStaff && (
          <nav className="hidden items-center gap-1 md:flex">
            {NAV_LINKS.map((link) => (
              <Button key={link.to} variant="ghost" size="sm" asChild>
                <Link to={link.to}>{link.label}</Link>
              </Button>
            ))}
          </nav>
        )}

        {!isStaff && (
          <form onSubmit={handleSearch} className="ml-auto hidden max-w-sm flex-1 items-center sm:flex">
            <div className="relative w-full">
              <Search className="pointer-events-none absolute left-2.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search dosas, juices, meals..."
                className="pl-8"
              />
            </div>
          </form>
        )}

        <div className="ml-auto flex items-center gap-1 sm:ml-2">
          <Button variant="ghost" size="icon" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "dark" ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </Button>

          {isStaff && (
            <Button variant="ghost" size="sm" className="hidden sm:inline-flex" asChild>
              <Link to={STAFF_DASHBOARD_PATH[user.role]}>
                <LayoutDashboard className="h-4 w-4" /> Dashboard
              </Link>
            </Button>
          )}

          {!isStaff && isAuthenticated && <NotificationsBell />}

          {!isStaff && (
            <Button variant="ghost" size="icon" asChild aria-label="Wishlist">
              <Link to="/wishlist">
                <Heart className="h-5 w-5" />
              </Link>
            </Button>
          )}

          {!isStaff && (
            <Button variant="ghost" size="icon" className="relative" asChild aria-label="Cart">
              <Link to="/cart">
                <ShoppingCart className="h-5 w-5" />
                {itemCount > 0 && (
                  <Badge className="absolute -right-1 -top-1 h-5 min-w-5 justify-center rounded-full px-1 text-[10px]">
                    {itemCount}
                  </Badge>
                )}
              </Link>
            </Button>
          )}

          {isAuthenticated ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="outline" size="sm" className="hidden sm:inline-flex">
                  {user?.full_name.split(" ")[0]}
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuLabel>{user?.full_name}</DropdownMenuLabel>
                <DropdownMenuSeparator />
                {!isStaff && (
                  <>
                    <DropdownMenuItem asChild>
                      <Link to="/orders">My Orders</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/wishlist">Wishlist</Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/profile">Profile & Addresses</Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                  </>
                )}
                <DropdownMenuItem onClick={logout}>Log out</DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <Button size="sm" className="hidden sm:inline-flex" asChild>
              <Link to="/login">Sign in</Link>
            </Button>
          )}

          <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
            <SheetTrigger asChild>
              <Button variant="ghost" size="icon" className="md:hidden" aria-label="Menu">
                <Menu className="h-5 w-5" />
              </Button>
            </SheetTrigger>
            <SheetContent side="right" className="w-72">
              {!isStaff && (
                <>
                  <form onSubmit={handleSearch} className="mt-8 flex items-center gap-2">
                    <Input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Search foods..." />
                    <Button type="submit" size="icon" variant="secondary" aria-label="Search">
                      <Search className="h-4 w-4" />
                    </Button>
                  </form>
                  <Separator className="my-4" />
                </>
              )}
              <nav className="flex flex-col gap-1">
                {isStaff ? (
                  <Button variant="ghost" className="justify-start" asChild onClick={() => setMobileOpen(false)}>
                    <Link to={STAFF_DASHBOARD_PATH[user.role]}>
                      <LayoutDashboard className="h-4 w-4" /> Dashboard
                    </Link>
                  </Button>
                ) : (
                  NAV_LINKS.map((link) => (
                    <Button key={link.to} variant="ghost" className="justify-start" asChild onClick={() => setMobileOpen(false)}>
                      <Link to={link.to}>{link.label}</Link>
                    </Button>
                  ))
                )}
                {isAuthenticated ? (
                  <>
                    {!isStaff && (
                      <>
                        <Button variant="ghost" className="justify-start" asChild onClick={() => setMobileOpen(false)}>
                          <Link to="/wishlist">Wishlist</Link>
                        </Button>
                        <Button variant="ghost" className="justify-start" asChild onClick={() => setMobileOpen(false)}>
                          <Link to="/profile">Profile & Addresses</Link>
                        </Button>
                      </>
                    )}
                    <Button variant="ghost" className="justify-start" onClick={logout}>
                      Log out
                    </Button>
                  </>
                ) : (
                  <Button className="justify-start" asChild onClick={() => setMobileOpen(false)}>
                    <Link to="/login">Sign in</Link>
                  </Button>
                )}
              </nav>
            </SheetContent>
          </Sheet>
        </div>
      </div>
    </header>
  );
}
