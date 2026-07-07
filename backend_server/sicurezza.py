import asyncio
import json
import websockets
import logging
import psutil
from googlesearch import search # Modulo ricerca

# Importazione moduli
import visione_reale as visione
import agente_proattivo
import fabbrica

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NucleoCentrale")

def cerca_su_google(query):
    try:
        risultati = list(search(query, num_results=1))
        return f"Ho trovato questo per te: {risultati[0]}" if risultati else "Nessun risultato trovato."
    except Exception as e:
        return f"Errore nella ricerca: {e}"

async def handler(websocket):
    logger.info("Connessione stabilita.")
    
    async def inviatore():
        try:
            while True:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                
                # Logica proattiva
                domanda = "Carico elevato: vuoi eseguire pulizia?" if cpu > 85 else "Sistema ok."
                
                dati = {
                    "sicurezza": "ALLERTA" if cpu > 85 else "NORMALE",
                    "visione": visione.scansiona(),
                    "monitoraggio": {"cpu": cpu, "ram": mem},
                    "domanda": domanda
                }
                await websocket.send(json.dumps(dati))
                await asyncio.sleep(2)
        except: pass

    async def ricevitore():
        try:
            async for message in websocket:
                comando = json.loads(message)
                logger.info(f"Comando ricevuto: {comando}")
                
                risposta = ""
                
                # 1. Azione: Pulizia
                if comando.get("azione") == "pulisci":
                    risposta = fabbrica.pulisci_file_temporanei()
                
                # 2. Azione: Comando testuale o vocale
                elif "comando_testuale" in comando:
                    testo = comando["comando_testuale"].lower()
                    if "pulisci" in testo:
                        risposta = fabbrica.pulisci_file_temporanei()
                    elif "cerca" in testo:
                        query = testo.replace("cerca", "").strip()
                        risposta = cerca_su_google(query)
                    else:
                        risposta = f"Ho ricevuto: {testo}. Per ora posso pulire il PC o cercare su Google."
                
                # Invio feedback all'app (che poi lo leggerà ad alta voce)
                if risposta:
                    await websocket.send(json.dumps({"feedback": risposta}))
        except: pass

    await asyncio.gather(inviatore(), ricevitore())

async def avvio_sistema():
    asyncio.create_task(agente_proattivo.avvia_battito())
    async with websockets.serve(handler, "127.0.0.1", 8080):
        logger.info("IA Guardiano Online (Porta 8080).")
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(avvio_sistema())