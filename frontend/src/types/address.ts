export interface Address {
  id: string;
  label: string;
  building: string | null;
  hostel: string | null;
  block: string | null;
  room_number: string | null;
  department: string | null;
  notes: string | null;
  latitude: number;
  longitude: number;
  is_default: boolean;
}

export interface AddressInput {
  label: string;
  building?: string | null;
  hostel?: string | null;
  block?: string | null;
  room_number?: string | null;
  department?: string | null;
  notes?: string | null;
  latitude: number;
  longitude: number;
  is_default?: boolean;
}
