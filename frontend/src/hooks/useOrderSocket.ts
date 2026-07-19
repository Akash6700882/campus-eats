import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { tokenStorage } from "@/lib/api";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";

export function useOrderSocket(orderId: string | undefined) {
  const queryClient = useQueryClient();

  useEffect(() => {
    if (!orderId) return;
    const token = tokenStorage.getAccess();
    if (!token) return;

    const socket = new WebSocket(`${WS_BASE_URL}/api/v1/ws/orders/${orderId}?token=${token}`);
    socket.onmessage = () => {
      queryClient.invalidateQueries({ queryKey: ["orders", orderId] });
    };

    return () => socket.close();
  }, [orderId, queryClient]);
}
