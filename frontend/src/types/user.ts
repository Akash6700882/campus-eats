export type Role = "customer" | "admin" | "kitchen" | "delivery";

export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role: Role;
  is_verified: boolean;
}
