import { api } from "@/lib/api";
import type { Category, CategoryInput, Food, FoodInput, FoodSearchParams } from "@/types";

export const menuApi = {
  listCategories: () => api.get<Category[]>("/categories").then((r) => r.data),
  searchFoods: (params: FoodSearchParams = {}) => api.get<Food[]>("/foods", { params }).then((r) => r.data),
  getFood: (slug: string) => api.get<Food>(`/foods/${slug}`).then((r) => r.data),
};

export const adminMenuApi = {
  createCategory: (payload: CategoryInput) =>
    api.post<Category>("/admin/categories", payload).then((r) => r.data),
  updateCategory: (id: string, payload: Partial<CategoryInput>) =>
    api.patch<Category>(`/admin/categories/${id}`, payload).then((r) => r.data),
  deleteCategory: (id: string) => api.delete(`/admin/categories/${id}`),
  createFood: (payload: FoodInput) => api.post<Food>("/admin/foods", payload).then((r) => r.data),
  updateFood: (id: string, payload: Partial<FoodInput>) =>
    api.patch<Food>(`/admin/foods/${id}`, payload).then((r) => r.data),
  deleteFood: (id: string) => api.delete(`/admin/foods/${id}`),
};
