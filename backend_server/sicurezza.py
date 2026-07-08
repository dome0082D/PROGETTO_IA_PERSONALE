import asyncio
import json
import websockets
import logging
import psutil
import random
import cv2
from googlesearch import search

# Importazione moduli
import visione_reale as visione
import agente_proattivo
import fabbrica

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NucleoCentrale")

# Lista di domande per stimolare l'apprendimento
domande_di_apprendimento = [
    "Cosa hai imparato di nuovo oggi che dovremmo archiviare?",
    "C'è un progetto su cui vuoi che focalizzi la mia memoria?",
    "Hai un'informazione recente da farmi assimilare?",
    "Come posso migliorare la mia assistenza per il tuo flusso di lavoro?"
]

def scansiona_sicura():
    """Controlla se la webcam esiste prima di scansionare."""
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "Visione Spaziale: NON DISPONIBILE"
    cap.release()
    return visione.scansiona()

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
                
                # Logica proattiva: domandi ogni tanto o avvisi se carico alto
                if cpu > 85:
                    domanda = "Carico elevato: vuoi eseguire pulizia?"
                elif random.random() < 0.05: # 5% di probabilità di fare una domanda
                    domanda = random.choice(domande_di_apprendimento)
                else:
                    domanda = "Sistema ok."
                
                dati = {
                    "sicurezza": "ALLERTA" if cpu > 85 else "NORMALE",
                    "visione": scansiona_sicura(),
                    "monitoraggio": {"cpu": cpu, "ram": mem},
                    "domanda": domanda
                }
                await websocket.send(json.dumps(dati))
                await asyncio.sleep(5) # Aumentato leggermente per non saturare
        except: pass

    async def ricevitore():
        try:
            async for message in websocket:
                comando = json.loads(message)
                logger.info(f"Comando ricevuto: {comando}")
                
                risposta = ""
                
                if comando.get("azione") == "pulisci":
                    risposta = fabbrica.pulisci_file_temporanei()
                
                elif "comando_testuale" in comando:
                    testo = comando["comando_testuale"].lower()
                    
                    if "pulisci" in testo:
                        risposta = fabbrica.pulisci_file_temporanei()
                    elif "cerca" in testo:
                        query = testo.replace("cerca", "").strip()
                        risposta = cerca_su_google(query)
                    else:
                        # Risposta conversazionale per archiviare
                        risposta = f"Interessante: {testo}. Ho registrato questa tua riflessione nel mio database."
                
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