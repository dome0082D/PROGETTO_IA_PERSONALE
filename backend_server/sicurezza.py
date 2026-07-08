import asyncio
import json
import websockets
import logging
import psutil
import random
import cv2
from googlesearch import search

# Importazione moduli personalizzati
import visione_reale as visione
import visione_intelligente as visione_ai # <--- NUOVO: Modulo OCR
import agente_proattivo
import fabbrica
import memoria

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NucleoCentrale")

domande_di_apprendimento = [
    "Cosa hai imparato di nuovo oggi che dovremmo archiviare?",
    "C'è un progetto su cui vuoi che focalizzi la mia memoria?",
    "Hai un'informazione recente da farmi assimilare?",
    "Come posso migliorare la mia assistenza per il tuo flusso di lavoro?"
]

def scansiona_sicura():
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
                
                if cpu > 85:
                    domanda = "Carico elevato: vuoi eseguire pulizia?"
                elif random.random() < 0.05:
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
                await asyncio.sleep(5)
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
                
                # 2. Azione: Analisi Immagini (Fase 2)
                elif "file_caricato" in comando:
                    percorso = comando["file_caricato"]
                    risposta = visione_ai.analizza_file(percorso)
                    risposta = f"Ho analizzato il file: {risposta}"
                
                # 3. Azione: Conversazione e Memoria
                elif "comando_testuale" in comando:
                    testo = comando["comando_testuale"].lower()
                    if "pulisci" in testo:
                        risposta = fabbrica.pulisci_file_temporanei()
                    elif "cerca" in testo:
                        query = testo.replace("cerca", "").strip()
                        risposta = cerca_su_google(query)
                    else:
                        risposta = memoria.salva_informazione(comando["comando_testuale"])
                        risposta = f"Ho memorizzato: {comando['comando_testuale']}. Sono qui per imparare da te."
                
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