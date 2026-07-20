export interface DeliveryPartner {
  id: string;
  user_id: string;
  full_name: string;
  phone: string;
  vehicle_number: string | null;
  is_available: boolean;
  current_latitude: number | null;
  current_longitude: number | null;
  rating_avg: number;
  total_deliveries: number;
  today_earnings: number;
}

export interface DeliveryLocationUpdate {
  latitude?: number;
  longitude?: number;
  is_available?: boolean;
}

export interface DeliveryPartnerCreateInput {
  user_id: string;
  vehicle_number?: string | null;
}
