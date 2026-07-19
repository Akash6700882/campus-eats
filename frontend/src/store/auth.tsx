import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { authApi, type TokenResponse } from "@/api/auth";
import { tokenStorage } from "@/lib/api";
import type { User } from "@/types";

interface SignupPayload {
  full_name: string;
  email: string;
  phone: string;
  password: string;
}

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<User>;
  loginWithOtp: (phone: string, otpCode: string) => Promise<User>;
  signup: (payload: SignupPayload) => Promise<User>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const queryClient = useQueryClient();

  useEffect(() => {
    let cancelled = false;

    async function loadUser() {
      if (!tokenStorage.getAccess()) {
        setIsLoading(false);
        return;
      }
      try {
        const me = await authApi.me();
        if (!cancelled) setUser(me);
      } catch {
        tokenStorage.clear();
      } finally {
        if (!cancelled) setIsLoading(false);
      }
    }

    void loadUser();
    return () => {
      cancelled = true;
    };
  }, []);

  async function applyTokens(tokens: TokenResponse): Promise<User> {
    tokenStorage.set(tokens.access_token, tokens.refresh_token);
    const me = await authApi.me();
    setUser(me);
    return me;
  }

  const login = (email: string, password: string) => authApi.login({ email, password }).then(applyTokens);
  const loginWithOtp = (phone: string, otpCode: string) => authApi.verifyOtp(phone, otpCode).then(applyTokens);
  const signup = (payload: SignupPayload) => authApi.signup(payload).then(applyTokens);

  const logout = () => {
    tokenStorage.clear();
    setUser(null);
    queryClient.clear();
  };

  return (
    <AuthContext.Provider
      value={{ user, isLoading, isAuthenticated: user !== null, login, loginWithOtp, signup, logout }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
