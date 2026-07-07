import asyncio
import websockets
import json
import psutil
import logging
import sys

# Importazione dei moduli che abbiamo creato
import memoria
import agente_proattivo
import visione_reale as visione
import empatia
import sogno
import fabbrica
import domotica

# Configurazione Log per monitorare l'attività
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("NucleoCentrale")

# --- Protocollo Zero: Controllo Hardware ---
def protocollo_zero():
    logger.info("Protocollo Zero: Avvio verifica integrità hardware...")
    if psutil.cpu_count() < 1:
        logger.error("Hardware instabile rilevato.")
        sys.exit(1)
    logger.info("Protocollo Zero completato: Sistema Sicuro.")

# --- Gestione Connessione WebSocket ---
async def handler(websocket):
    logger.info("Connessione stabilita con l'Interfaccia Viva.")
    try:
        while True:
            # Rilevazione dati dai moduli
            stato_visione = visione.scansiona()
            cpu_uso = psutil.cpu_percent(interval=1)
            mem_uso = psutil.virtual_memory().percent
            
            # Creazione del pacchetto dati completo
            dati = {
                "sicurezza": "NORMALE",
                "visione": stato_visione,
                "monitoraggio": {
                    "cpu": cpu_uso,
                    "ram": mem_uso
                }
            }
            
            # Invio all'app Flutter
            await websocket.send(json.dumps(dati))
            await asyncio.sleep(0.5)
    except websockets.exceptions.ConnectionClosed:
        logger.info("Connessione terminata.")

# --- Avvio Sistema ---
async def avvio_sistema():
    protocollo_zero()
    
    # Avvio del "Battito Cardiaco" in background (24/7)
    asyncio.create_task(agente_proattivo.avvia_battito())
    
    logger.info("IA Guardiano Online. In attesa di input.")
    
    # Avvio Server WebSocket
    async with websockets.serve(handler, "127.0.0.1", 8080):
        await asyncio.Future() # Mantiene il server attivo indefinitamente

if __name__ == "__main__":
    try:
        asyncio.run(avvio_sistema())
    except KeyboardInterrupt:
        logger.info("Spegnimento sistema richiesto.")