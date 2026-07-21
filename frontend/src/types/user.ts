export type Role = "customer" | "admin" | "kitchen" | "delivery";

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role: Role;
  is_verified: boolean;
}

export interface AdminUser {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role: Role;
  is_active: boolean;
}

export interface AdminCustomer {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  is_active: boolean;
  total_orders: number;
  total_spend: number;
  last_order_at: string | null;
}
