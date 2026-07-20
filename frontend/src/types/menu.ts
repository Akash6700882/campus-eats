export interface Category {
  id: string;
  name: string;
  slug: string;
  description: string | null;
  image_url: string | null;
  sort_order: number;
  is_active: boolean;
}

export interface Food {
  id: string;
  category_id: string;
  category_name: string;
  name: string;
  slug: string;
  description: string | null;
  image_url: string | null;
  price: number;
  discount_percent: number;
  discounted_price: number;
  is_veg: boolean;
  prep_time_minutes: number;
  rating_avg: number;
  rating_count: number;
  is_available: boolean;
  is_popular: boolean;
  is_special_today: boolean;
}

export interface FoodSearchParams {
  q?: string;
  category_id?: string;
  min_price?: number;
  max_price?: number;
  min_rating?: number;
  is_veg?: boolean;
  is_popular?: boolean;
  is_special_today?: boolean;
  limit?: number;
  offset?: number;
}

export interface CategoryInput {
  name: string;
  description?: string | null;
  image_url?: string | null;
  sort_order?: number;
  is_active?: boolean;
}

export interface FoodInput {
  category_id: string;
  name: string;
  description?: string | null;
  image_url?: string | null;
  price: number;
  discount_percent?: number;
  is_veg?: boolean;
  prep_time_minutes?: number;
  is_available?: boolean;
  is_popular?: boolean;
  is_special_today?: boolean;
}
