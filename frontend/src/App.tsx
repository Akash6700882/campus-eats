import { BrowserRouter, Route, Routes } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/sonner";
import { queryClient } from "@/lib/queryClient";
import { ThemeProvider } from "@/store/theme";
import { AuthProvider } from "@/store/auth";
import { AppLayout } from "@/components/layout/AppLayout";
import { ProtectedRoute } from "@/components/ProtectedRoute";
import { RoleProtectedRoute } from "@/components/RoleProtectedRoute";
import { HomePage } from "@/pages/customer/HomePage";
import { LoginPage } from "@/pages/customer/LoginPage";
import { SignupPage } from "@/pages/customer/SignupPage";
import { MenuPage } from "@/pages/customer/MenuPage";
import { CartPage } from "@/pages/customer/CartPage";
import { CheckoutPage } from "@/pages/customer/CheckoutPage";
import { OrderTrackingPage } from "@/pages/customer/OrderTrackingPage";
import { OrderHistoryPage } from "@/pages/customer/OrderHistoryPage";
import { ProfilePage } from "@/pages/customer/ProfilePage";
import { WishlistPage } from "@/pages/customer/WishlistPage";
import { DeliveryDashboardPage } from "@/pages/delivery/DeliveryDashboardPage";
import { AdminDashboardPage } from "@/pages/admin/AdminDashboardPage";

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <BrowserRouter>
          <AuthProvider>
            <AppLayout>
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/signup" element={<SignupPage />} />
                <Route path="/menu" element={<MenuPage />} />
                <Route path="/cart" element={<CartPage />} />
                <Route
                  path="/checkout"
                  element={
                    <ProtectedRoute>
                      <CheckoutPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/orders"
                  element={
                    <ProtectedRoute>
                      <OrderHistoryPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/orders/:id"
                  element={
                    <ProtectedRoute>
                      <OrderTrackingPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/profile"
                  element={
                    <ProtectedRoute>
                      <ProfilePage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/wishlist"
                  element={
                    <ProtectedRoute>
                      <WishlistPage />
                    </ProtectedRoute>
                  }
                />
                <Route
                  path="/delivery"
                  element={
                    <RoleProtectedRoute roles={["delivery", "admin"]}>
                      <DeliveryDashboardPage />
                    </RoleProtectedRoute>
                  }
                />
                <Route
                  path="/admin"
                  element={
                    <RoleProtectedRoute roles={["admin"]}>
                      <AdminDashboardPage />
                    </RoleProtectedRoute>
                  }
                />
              </Routes>
            </AppLayout>
            <Toaster richColors position="top-center" />
          </AuthProvider>
        </BrowserRouter>
      </ThemeProvider>
    </QueryClientProvider>
  );
}
