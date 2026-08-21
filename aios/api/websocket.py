"""WebSocket gateway — EventBus → EventService → Gateway → Client (TASK-017).

Layering: ``api`` layer.
"""
from __future__ import annotations

import asyncio
import json
import threading
from typing import Any, Dict, List, Optional, Set

from fastapi import WebSocket, WebSocketDisconnect

from .events import EventEnvelope, EventService


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: Set[WebSocket] = set()
        self._lock = threading.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        with self._lock:
            self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        with self._lock:
            self._connections.discard(websocket)

    async def send(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        try:
            await websocket.send_json(message)
        except Exception:
            pass

    async def broadcast(self, message: Dict[str, Any]) -> None:
        with self._lock:
            conns = list(self._connections)
        for ws in conns:
            try:
                await ws.send_json(message)
            except Exception:
                with self._lock:
                    self._connections.discard(ws)

    @property
    def count(self) -> int:
        with self._lock:
            return len(self._connections)


class WebSocketGateway:
    def __init__(self, event_service: Optional[EventService] = None,
                 manager: Optional[ConnectionManager] = None) -> None:
        self.event_service = event_service or EventService()
        self.manager = manager or ConnectionManager()
        self._subscribed = False
        self._lock = threading.Lock()

    def _on_event(self, envelope: EventEnvelope) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        try:
            loop.create_task(self.manager.broadcast(envelope.to_dict()))
        except Exception:
            pass

    def start(self) -> None:
        with self._lock:
            if not self._subscribed:
                self.event_service.subscribe(self._on_event)
                self._subscribed = True

    def stop(self) -> None:
        with self._lock:
            if self._subscribed:
                try:
                    self.event_service.unsubscribe(self._on_event)
                except Exception:
                    pass
                self._subscribed = False

    async def handle_connection(self, websocket: WebSocket, last_event_id: Optional[str] = None) -> None:
        await self.manager.connect(websocket)
        if last_event_id:
            for env in self.event_service.replay_since(last_event_id):
                await self.manager.send(websocket, env.to_dict())
        else:
            for env in self.event_service.history(limit=10):
                await self.manager.send(websocket, env.to_dict())
        try:
            while True:
                data = await websocket.receive_text()
                try:
                    msg = json.loads(data)
                    if isinstance(msg, dict) and msg.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
                except json.JSONDecodeError:
                    pass
        except WebSocketDisconnect:
            pass
        except Exception:
            pass
        finally:
            self.manager.disconnect(websocket)
