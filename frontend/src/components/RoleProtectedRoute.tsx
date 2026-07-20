import type { ReactNode } from "react";
import { Navigate } from "react-router-dom";
import { PageSpinner } from "@/components/PageSpinner";
import { useAuth } from "@/store/auth";
import type { Role } from "@/types";

export function RoleProtectedRoute({ roles, children }: { roles: Role[]; children: ReactNode }) {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) return <PageSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (!user || !roles.includes(user.role)) return <Navigate to="/" replace />;
  return <>{children}</>;
}
