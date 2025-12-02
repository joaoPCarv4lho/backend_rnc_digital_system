from typing import Dict, Set
from jose import jwt, JWTError
from fastapi import WebSocket
import logging
import json
from app.core.config import settings

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
        self.groups: Dict[str, Set[WebSocket]] = {
            "admin": set(),
            "qualidade": set(),
            "engenharia": set(),
            "operador": set(),
            "tecnico": set()
        }
        self.user_map: Dict[int, WebSocket] = {}
        self.ws_to_user: Dict[WebSocket, int] = {}
    
    async def connect(self, websocket: WebSocket, token: str):

        logger.warning(f"[DEBUG] Token recebido no WebSocket: {token}")
        user_data = self._decode_token(token)
        
        if not user_data:
            raise RuntimeError("Token inválido")

        if "user_id" not in user_data or "role" not in user_data:
            raise RuntimeError("Token não cotém campos obrigatórios (id, role)")
        user_id = user_data["user_id"]
        role = user_data["role"]

        if role not in self.groups:
            raise RuntimeError(f"Role inválido: {role}")
        
        await websocket.accept()

        self.active_connections.add(websocket)
        self.groups[role].add(websocket)
        self.user_map[user_id] = websocket
        self.ws_to_user[websocket] = { "user_id": user_id, "role": role }

        logger.info(f"User {user_id} ({role}) conectado via WebSocket")
        return user_data
    
    def _decode_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

            logger.debug(f"Token decodificado: user_id={payload.get('user_id')}, role={payload.get('role')}")
            return payload
        except JWTError as e:
            logger.error(f"Erro ao decodificar token: {type(e).__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado ao decodificar token: {e}")
            return None
    
    async def broadcast_all(self, event: str, payload: dict):
        message = json.dumps({"type": event, "payload": payload})
        disconnected = []

        logger.info(f"Broadcasting '{event}' para {len(self.active_connections)}")

        for ws in list(self.active_connections):
            try:
                await ws.send_text(message)
            except Exception as e:
                user_data = self.ws_to_user.get(ws, {})
                user_id = user_data.get("user_id", "unknown")
                logger.warning(f"Falha ao enviar para user {user_id}: {e}")
                disconnected.append(ws)
            for ws in disconnected:
                self.disconnect(ws)
    
    async def broadcast_group(self, role: str, event: str, payload: dict):
        message = json.dumps({"type": event, "payload": payload})
        disconnected = []

        connections = self.groups.get(role, set())
        logger.info(f"Broadcasting '{event}' para grupo '{role}' ({len(connections)}) conexões")

        for ws in list(self.groups.get(role, [])):
            try:
                await ws.send_text(message)
            except Exception as e:
                user_data = self.ws_to_user.get(ws, {})
                user_id = user_data.get("user_id", "unknown")
                logger.warning(f"Falha ao enviar para user {user_id}: {e}")
                disconnected.append(ws)
        for ws in disconnected:
            self.disconnect(ws)

    def disconnect(self, websocket: WebSocket):
        user_data = self.ws_to_user.get(websocket, {})
        user_id = user_data.get('user_id', 'unknown')

        self.active_connections.discard(websocket)

        for group in self.groups.values():
            group.discard(websocket)

        if websocket in self.ws_to_user:
            del self.ws_to_user[websocket]
        if user_id != 'unknown' and user_id in self.user_map:
            del self.user_map[user_id]

        logger.info(f"User {user_id} desconectado")

manager = ConnectionManager()