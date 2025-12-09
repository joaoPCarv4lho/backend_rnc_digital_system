from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status
from .manager import manager
import logging
import traceback

logger = logging.getLogger(__name__)

ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

router = APIRouter()

@router.websocket('/rncs')
async def websocket_endpoint(websocket: WebSocket):
    user_data = None

    try:
        origin = websocket.headers.get("origin")
        logger.info(f"WebSocket - Origem: {origin}")

        if origin and origin not in ALLOWED_ORIGINS:
            logger.warning(f"Origem não permitida: {origin}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Origin not allowed")
            return
        
        logger.info(f"Nova tentativa de conexão WebSocket de {websocket.client}")
        logger.info(f"Cliente: {websocket.client}")
        logger.info(f"Headers: {dict(websocket.headers)}")

        token = websocket.query_params.get("token")
        if not token:
            logger.warning("WebSocket rejeitado: token ausente")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Token missing")
            return
        
        logger.info(f"Token recebido (primeiros 20 chars): {token[:20]}...")
    
        try:
            user_data = await manager.connect(websocket, token=token)
            logger.info(f"WebSocket conectado - User ID: {user_data.get('user_id')}, Role: {user_data.get('role')}")
        except RuntimeError as e:
            logger.error(f"Erro de autenticação: {e}")
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
        except Exception as e:
            logger.error(f"Erro inesperado na autenticação: {e}")
            logger.error(traceback.format_exc())
            await websocket.close(code=status.WS_1011_INTERNAL_ERROR, reason="Auth error")
            return

        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"Mensagem recebida do cliente {user_data.get('user_id')}: {data}")
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                logger.info(f"Cliente {user_data.get('user_id')} desconectou normalmente")
                break
    except Exception as e:
        logger.error(f"Erro no WebSocket: {type(e).__name__}: {e}")
        logger.error(traceback.format_exc())
    finally:
        if user_data:
            logger.info(f"Limpando conexão do user {user_data.get('user_id')}")
        manager.disconnect(websocket)