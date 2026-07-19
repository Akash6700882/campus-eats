export interface PaymentInitiateResponse {
  payment_id: string;
  razorpay_order_id: string;
  razorpay_key_id: string;
  amount: number;
  currency: string;
}

export type PaymentStatus = "created" | "pending" | "paid" | "failed" | "refunded";

export interface PaymentResponse {
  id: string;
  order_id: string;
  status: PaymentStatus;
  amount: number;
  currency: string;
  provider_order_id: string | null;
  provider_payment_id: string | null;
  failure_reason: string | null;
}

export interface PaymentVerifyRequest {
  razorpay_order_id: string;
  razorpay_payment_id: string;
  razorpay_signature: string;
}
