import asyncio
import websockets
import json
import psutil
import logging
import sys

# Configurazione del sistema di logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SicurezzaServer")

async def handler(websocket, path):
    """
    Gestisce la connessione WebSocket.
    Ogni volta che Flutter si connette, questo handler mantiene
    un ciclo infinito di invio dati fino a disconnessione.
    """
    client_address = websocket.remote_address
    logger.info(f"Connessione stabilita con client: {client_address}")
    
    try:
        while True:
            # Rilevamento dati hardware completo
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_info = psutil.virtual_memory()
            
            # Struttura del pacchetto dati completa
            dati_sistema = {
                "tipo": "monitoraggio_sistema",
                "cpu": {
                    "percentuale": cpu_percent,
                    "frequenza": psutil.cpu_freq().current if psutil.cpu_freq() else 0
                },
                "memoria": {
                    "totale_gb": round(memory_info.total / (1024**3), 2),
                    "percentuale": memory_info.percent
                },
                "stato": "attivo"
            }
            
            # Invio dei dati al client
            await websocket.send(json.dumps(dati_sistema))
            
            # Intervallo di monitoraggio
            await asyncio.sleep(1)
            
    except websockets.exceptions.ConnectionClosed:
        logger.warning(f"Connessione chiusa con: {client_address}")
    except Exception as e:
        logger.error(f"Errore critico durante la gestione del client {client_address}: {e}")

async def avvio_server():
    """Inizializza e mantiene attivo il server WebSocket."""
    logger.info("Inizializzazione del server WebSocket...")
    
    # Avvio del server su 127.0.0.1 porta 8080
    server = await websockets.serve(handler, "127.0.0.1", 8080)
    
    logger.info("Server WebSocket avviato con successo su ws://127.0.0.1:8080")
    logger.info("In attesa di connessioni...")
    
    # Mantiene il server in attesa di segnali
    await server.wait_closed()

if __name__ == "__main__":
    # Controllo versione Python per compatibilità
    if sys.version_info < (3, 7):
        logger.error("Questo script richiede Python 3.7 o superiore.")
        sys.exit(1)
        
    try:
        # Recupero del loop di eventi
        loop = asyncio.get_event_loop()
        loop.run_until_complete(avvio_server())
    except KeyboardInterrupt:
        logger.info("Server interrotto manualmente dall'utente.")
    except Exception as e:
        logger.error(f"Errore fatale nell'avvio del server: {e}")