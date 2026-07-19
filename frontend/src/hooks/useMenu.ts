import { useQuery } from "@tanstack/react-query";
import { menuApi } from "@/api/menu";
import type { FoodSearchParams } from "@/types";

export function useCategories() {
  return useQuery({ queryKey: ["categories"], queryFn: menuApi.listCategories });
}

export function useFoods(params: FoodSearchParams) {
  return useQuery({
    queryKey: ["foods", params],
    queryFn: () => menuApi.searchFoods(params),
  });
}
