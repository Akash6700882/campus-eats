import { LayoutDashboard } from "lucide-react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { AdminAnalyticsTab } from "@/pages/admin/AdminAnalyticsTab";
import { AdminOrdersTab } from "@/pages/admin/AdminOrdersTab";
import { AdminPartnersTab } from "@/pages/admin/AdminPartnersTab";
import { AdminMenuTab } from "@/pages/admin/AdminMenuTab";
import { AdminZoneTab } from "@/pages/admin/AdminZoneTab";

export function AdminDashboardPage() {
  return (
    <div className="container py-8">
      <h1 className="flex items-center gap-2 font-heading text-2xl font-bold">
        <LayoutDashboard className="h-6 w-6 text-primary" /> Admin dashboard
      </h1>

      <Tabs defaultValue="analytics" className="mt-6">
        <TabsList>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
          <TabsTrigger value="orders">Orders</TabsTrigger>
          <TabsTrigger value="partners">Delivery partners</TabsTrigger>
          <TabsTrigger value="menu">Menu</TabsTrigger>
          <TabsTrigger value="zone">Delivery zone</TabsTrigger>
        </TabsList>
        <TabsContent value="analytics" className="mt-4">
          <AdminAnalyticsTab />
        </TabsContent>
        <TabsContent value="orders" className="mt-4">
          <AdminOrdersTab />
        </TabsContent>
        <TabsContent value="partners" className="mt-4">
          <AdminPartnersTab />
        </TabsContent>
        <TabsContent value="menu" className="mt-4">
          <AdminMenuTab />
        </TabsContent>
        <TabsContent value="zone" className="mt-4">
          <AdminZoneTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
