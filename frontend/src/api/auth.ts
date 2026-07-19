import { api } from "@/lib/api";
import type { User } from "@/types";

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export const authApi = {
  signup: (payload: { full_name: string; email: string; phone: string; password: string }) =>
    api.post<TokenResponse>("/auth/signup", payload).then((r) => r.data),
  login: (payload: { email: string; password: string }) =>
    api.post<TokenResponse>("/auth/login", payload).then((r) => r.data),
  requestOtp: (phone: string) => api.post("/auth/otp/request", { phone }),
  verifyOtp: (phone: string, otp_code: string) =>
    api.post<TokenResponse>("/auth/otp/verify", { phone, otp_code }).then((r) => r.data),
  forgotPassword: (email: string) => api.post("/auth/forgot-password", { email }),
  resetPassword: (token: string, new_password: string) =>
    api.post("/auth/reset-password", { token, new_password }),
  me: () => api.get<User>("/auth/me").then((r) => r.data),
};
