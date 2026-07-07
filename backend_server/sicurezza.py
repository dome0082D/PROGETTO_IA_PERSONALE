import asyncio
import json
import websockets
import logging
import psutil

# Importazione dei tuoi moduli reali
import visione_reale as visione
import agente_proattivo
import memoria
import fabbrica

# Configurazione Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NucleoCentrale")

async def handler(websocket):
    logger.info("Connessione stabilita con l'Interfaccia Viva.")
    try:
        while True:
            # 1. Acquisizione Dati Reali
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory().percent
            
            # 2. Interrogazione Moduli
            stato_visione = visione.scansiona()
            
            # 3. Logica Proattiva (Agente che pone domande)
            domanda = "Sistema operativo. Tutto nella norma."
            if cpu > 85:
                domanda = "Carico elevato: vuoi che esegua una pulizia file temporanei?"
            
            # 4. Preparazione Pacchetto Dati
            dati = {
                "sicurezza": "ALLERTA" if cpu > 85 else "NORMALE",
                "visione": stato_visione,
                "monitoraggio": {"cpu": cpu, "ram": mem},
                "domanda": domanda
            }
            
            # 5. Invio all'Interfaccia Flutter
            await websocket.send(json.dumps(dati))
            await asyncio.sleep(2)
            
    except websockets.exceptions.ConnectionClosed:
        logger.info("Interfaccia disconnessa.")

async def avvio_sistema():
    # Avvia il task dell'agente proattivo in background
    asyncio.create_task(agente_proattivo.avvia_battito())
    
    # Avvia il server WebSocket
    async with websockets.serve(handler, "127.0.0.1", 8080):
        logger.info("IA Guardiano Online sulla porta 8080...")
        await asyncio.Future()  # Mantiene il server in vita

if __name__ == "__main__":
    try:
        asyncio.run(avvio_sistema())
    except KeyboardInterrupt:
        logger.info("Spegnimento sistema richiesto.")