import asyncio
import websockets
import json
import psutil
import logging
import sys
from memoria import MemoriaApprendimento
from agente_proattivo import battito_cardiaco

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("SicurezzaServer")

class GuardianoDigitale:
    def __init__(self):
        self.memoria = MemoriaApprendimento()
    
    def analizza_comportamento(self, cpu_uso):
        if cpu_uso > 95:
            return "ALTA_ATTENZIONE"
        return "NORMALE"

guardiano = GuardianoDigitale()

async def handler(websocket):
    client_address = websocket.remote_address
    logger.info(f"Connessione stabilita con: {client_address}")
    
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            mem = psutil.virtual_memory()
            stato = guardiano.analizza_comportamento(cpu)
            
            dati = {
                "sicurezza": stato,
                "monitoraggio": {"cpu": cpu, "ram": mem.percent}
            }
            await websocket.send(json.dumps(dati))
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Errore: {e}")

async def avvio_sistema():
    logger.info("Protocollo Zero: Avvio sicuro...")
    # Avvio del battito in background
    asyncio.create_task(battito_cardiaco(guardiano))
    
    async with websockets.serve(handler, "127.0.0.1", 8080):
        logger.info("IA Guardiano Online.")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(avvio_sistema())