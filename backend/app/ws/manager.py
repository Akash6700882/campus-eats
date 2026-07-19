from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """In-memory pub/sub for live order-tracking WebSockets.

    Single-process only — correct for one uvicorn worker (this app's default
    dev/small-scale deployment). Running multiple backend replicas would need
    a shared broker (e.g. Redis pub/sub) to fan broadcasts out across workers.
    """

    def __init__(self) -> None:
        self._channels: dict[str, set[WebSocket]] = defaultdict(set)

    async def connect(self, channel: str, websocket: WebSocket) -> None:
        await websocket.accept()
        self._channels[channel].add(websocket)

    def disconnect(self, channel: str, websocket: WebSocket) -> None:
        self._channels[channel].discard(websocket)
        if not self._channels[channel]:
            self._channels.pop(channel, None)

    async def broadcast(self, channel: str, message: dict) -> None:
        dead = []
        for websocket in self._channels.get(channel, ()):
            try:
                await websocket.send_json(message)
            except Exception:
                dead.append(websocket)
        for websocket in dead:
            self.disconnect(channel, websocket)


manager = ConnectionManager()
