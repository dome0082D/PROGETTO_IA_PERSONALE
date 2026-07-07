import asyncio
import json
import websockets
import logging
import psutil

# Importazione moduli
import visione_reale as visione
import agente_proattivo
import memoria
import fabbrica

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NucleoCentrale")

async def handler(websocket):
    logger.info("Connessione stabilita.")
    
    # Task per inviare dati ogni 2 secondi
    async def inviatore():
        try:
            while True:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                dati = {
                    "sicurezza": "ALLERTA" if cpu > 85 else "NORMALE",
                    "visione": visione.scansiona(),
                    "monitoraggio": {"cpu": cpu, "ram": mem},
                    "domanda": "Carico elevato: vuoi eseguire pulizia?" if cpu > 85 else "Sistema ok."
                }
                await websocket.send(json.dumps(dati))
                await asyncio.sleep(2)
        except websockets.exceptions.ConnectionClosed:
            pass

    # Task per ricevere comandi dal frontend
    async def ricevitore():
        try:
            async for message in websocket:
                comando = json.loads(message)
                logger.info(f"Comando ricevuto: {comando}")
                
                # Esecuzione azioni reali in base al comando ricevuto
                if comando.get("azione") == "pulisci":
                    risultato = fabbrica.pulisci_file_temporanei()
                    await websocket.send(json.dumps({"feedback": risultato}))
        except websockets.exceptions.ConnectionClosed:
            pass

    # Esegui i due task in parallelo
    await asyncio.gather(inviatore(), ricevitore())

async def avvio_sistema():
    asyncio.create_task(agente_proattivo.avvia_battito())
    async with websockets.serve(handler, "127.0.0.1", 8080):
        logger.info("IA Guardiano Online (Porta 8080).")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(avvio_sistema())