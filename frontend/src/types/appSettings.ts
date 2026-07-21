export interface AppSettings {
  restaurant_name: string;
  gst_percent: number;
  delivery_charge: number;
  packing_charge: number;
  business_hours_open: string;
  business_hours_close: string;
}

export type AppSettingsInput = AppSettings;
