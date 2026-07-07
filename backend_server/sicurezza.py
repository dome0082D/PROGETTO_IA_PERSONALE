import asyncio
import websockets
import json
import psutil
import logging

# Configurazione del sistema di logging per tracciare ogni errore
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SicurezzaServer")

async def handler(websocket, path):
    """Gestisce la connessione WebSocket e il flusso dei dati hardware."""
    client_address = websocket.remote_address
    logger.info(f"Connessione stabilita con: {client_address}")
    
    try:
        while True:
            # Rilevamento dati hardware completo
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            
            # Struttura del pacchetto dati completa
            dati_sistema = {
                "tipo": "stato_sistema",
                "timestamp": asyncio.get_event_loop().time(),
                "cpu": {
                    "percentuale": cpu_percent,
                    "core_count": psutil.cpu_count()
                },
                "memoria": {
                    "totale": memory_info.total,
                    "disponibile": memory_info.available,
                    "percentuale": memory_info.percent
                },
                "messaggio": "Monitoraggio attivo e in apprendimento"
            }
            
            # Invio dei dati al client
            await websocket.send(json.dumps(dati_sistema))
            
            # Intervallo di monitoraggio
            await asyncio.sleep(1)
            
    except websockets.exceptions.ConnectionClosed:
        logger.warning(f"Connessione chiusa con: {client_address}")
    except Exception as e:
        logger.error(f"Errore critico durante la gestione del client: {e}")

async def avvio_server():
    """Inizializza e mantiene attivo il server WebSocket."""
    server = await websockets.serve(handler, "127.0.0.1", 8080)
    logger.info("Server WebSocket avviato su ws://127.0.0.1:8080")
    await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(avvio_server())
    except KeyboardInterrupt:
        logger.info("Server interrotto dall'utente.")