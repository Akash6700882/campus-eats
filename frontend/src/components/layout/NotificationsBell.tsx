import { Bell, CheckCheck } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { useNotificationActions, useNotifications } from "@/hooks/useNotifications";
import { cn } from "@/lib/utils";
import { formatDateTime } from "@/lib/format";

export function NotificationsBell() {
  const { data } = useNotifications();
  const { markRead, markAllRead } = useNotificationActions();
  const unreadCount = data?.unread_count ?? 0;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" size="icon" className="relative" aria-label="Notifications">
          <Bell className="h-5 w-5" />
          {unreadCount > 0 && (
            <Badge className="absolute -right-1 -top-1 h-5 min-w-5 justify-center rounded-full px-1 text-[10px]">
              {unreadCount}
            </Badge>
          )}
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-80">
        <div className="flex items-center justify-between px-2 py-1">
          <DropdownMenuLabel className="p-0">Notifications</DropdownMenuLabel>
          {unreadCount > 0 && (
            <Button variant="ghost" size="sm" className="h-6 px-1.5 text-xs" onClick={() => markAllRead.mutate()}>
              <CheckCheck className="h-3 w-3" /> Mark all read
            </Button>
          )}
        </div>
        <DropdownMenuSeparator />
        <div className="max-h-80 overflow-y-auto">
          {(!data || data.items.length === 0) && (
            <p className="px-2 py-4 text-center text-sm text-muted-foreground">No notifications yet</p>
          )}
          {data?.items.map((notification) => (
            <DropdownMenuItem
              key={notification.id}
              className={cn("flex-col items-start gap-0.5 whitespace-normal", !notification.is_read && "bg-accent/50")}
              onClick={() => !notification.is_read && markRead.mutate(notification.id)}
            >
              <span className="text-sm font-medium">{notification.title}</span>
              <span className="text-xs text-muted-foreground">{notification.message}</span>
              <span className="text-[10px] text-muted-foreground">{formatDateTime(notification.created_at)}</span>
            </DropdownMenuItem>
          ))}
        </div>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
