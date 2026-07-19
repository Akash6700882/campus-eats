import { api } from "@/lib/api";
import type { Category, Food, FoodSearchParams } from "@/types";

export const menuApi = {
  listCategories: () => api.get<Category[]>("/categories").then((r) => r.data),
  searchFoods: (params: FoodSearchParams = {}) => api.get<Food[]>("/foods", { params }).then((r) => r.data),
  getFood: (slug: string) => api.get<Food>(`/foods/${slug}`).then((r) => r.data),
};
