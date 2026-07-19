import type { ReactNode } from "react";
import { Navigate, useLocation } from "react-router-dom";
import { PageSpinner } from "@/components/PageSpinner";
import { useAuth } from "@/store/auth";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) return <PageSpinner />;
  if (!isAuthenticated) return <Navigate to="/login" state={{ from: location }} replace />;
  return <>{children}</>;
}
