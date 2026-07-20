import type { Food } from "./menu";

export interface Review {
  id: string;
  food_id: string;
  user_id: string;
  user_name: string;
  rating: number;
  comment: string | null;
  image_url: string | null;
  likes_count: number;
  created_at: string;
}

export interface ReviewCreateInput {
  rating: number;
  comment?: string | null;
  image_url?: string | null;
  order_id?: string | null;
}

export interface ReviewLikeResult {
  review_id: string;
  liked: boolean;
  likes_count: number;
}

export interface WishlistItem {
  id: string;
  food: Food;
  created_at: string;
}

export type NotificationType = "order_update" | "promotion" | "system";

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  is_read: boolean;
  created_at: string;
}

export interface NotificationList {
  items: Notification[];
  unread_count: number;
}
