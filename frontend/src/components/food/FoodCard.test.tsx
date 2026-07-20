import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { FoodCard } from "./FoodCard";
import type { Food } from "@/types";

const addItemMutate = vi.fn();
const wishlistAddMutate = vi.fn();
const wishlistRemoveMutate = vi.fn();

vi.mock("@/hooks/useCart", () => ({
  useCartMutations: () => ({ addItem: { mutate: addItemMutate, isPending: false } }),
}));

let mockWishlist: { food: { id: string } }[] = [];
vi.mock("@/hooks/useWishlist", () => ({
  useWishlist: () => ({ data: mockWishlist }),
  useWishlistMutations: () => ({
    add: { mutate: wishlistAddMutate },
    remove: { mutate: wishlistRemoveMutate },
  }),
}));

let mockIsAuthenticated = true;
vi.mock("@/store/auth", () => ({
  useAuth: () => ({ isAuthenticated: mockIsAuthenticated }),
}));

vi.mock("@/hooks/useReviews", () => ({
  useFoodReviews: () => ({ data: [], isLoading: false }),
  useReviewActions: () => ({ create: { mutate: vi.fn(), isPending: false }, toggleLike: { mutate: vi.fn() } }),
}));

const food: Food = {
  id: "food-1",
  category_id: "cat-1",
  category_name: "South Indian",
  name: "Masala Dosa",
  slug: "masala-dosa",
  description: "Crispy dosa with potato masala",
  image_url: null,
  price: 70,
  discount_percent: 10,
  discounted_price: 63,
  is_veg: true,
  prep_time_minutes: 14,
  rating_avg: 4.5,
  rating_count: 12,
  is_available: true,
  is_popular: true,
  is_special_today: false,
};

describe("FoodCard", () => {
  beforeEach(() => {
    addItemMutate.mockClear();
    wishlistAddMutate.mockClear();
    wishlistRemoveMutate.mockClear();
    mockWishlist = [];
    mockIsAuthenticated = true;
  });

  it("renders the food's name, price, and discount", () => {
    render(<FoodCard food={food} />);
    expect(screen.getByText("Masala Dosa")).toBeInTheDocument();
    expect(screen.getByText("₹63.00")).toBeInTheDocument();
    expect(screen.getByText("₹70.00")).toBeInTheDocument();
    expect(screen.getByText("10% off")).toBeInTheDocument();
  });

  it("increments quantity and adds that quantity to the cart", () => {
    render(<FoodCard food={food} />);

    fireEvent.click(screen.getByLabelText("Increase quantity"));
    fireEvent.click(screen.getByText("Add to cart"));

    expect(addItemMutate).toHaveBeenCalledWith({ foodId: "food-1", quantity: 2 });
  });

  it("does not let quantity go below 1", () => {
    render(<FoodCard food={food} />);
    expect(screen.getByLabelText("Decrease quantity")).toBeDisabled();
  });

  it("disables add to cart when the item is unavailable", () => {
    render(<FoodCard food={{ ...food, is_available: false }} />);
    expect(screen.getByText("Add to cart").closest("button")).toBeDisabled();
    expect(screen.getByText("Currently unavailable")).toBeInTheDocument();
  });

  it("adds to wishlist when the heart is clicked while signed in", () => {
    render(<FoodCard food={food} />);
    fireEvent.click(screen.getByLabelText("Add to wishlist"));
    expect(wishlistAddMutate).toHaveBeenCalledWith("food-1");
  });

  it("removes from wishlist when already wishlisted", () => {
    mockWishlist = [{ food: { id: "food-1" } }];
    render(<FoodCard food={food} />);
    fireEvent.click(screen.getByLabelText("Remove from wishlist"));
    expect(wishlistRemoveMutate).toHaveBeenCalledWith("food-1");
  });

  it("does not call the wishlist API when signed out", () => {
    mockIsAuthenticated = false;
    render(<FoodCard food={food} />);
    fireEvent.click(screen.getByLabelText("Add to wishlist"));
    expect(wishlistAddMutate).not.toHaveBeenCalled();
  });
});
