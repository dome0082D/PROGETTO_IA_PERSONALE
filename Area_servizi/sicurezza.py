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
import visione_intelligente as visione_ai
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
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return "Visione Spaziale: NON DISPONIBILE"
        _, frame = cap.read()
        cap.release()
        return visione.scansiona()
    except:
        return "Visione Spaziale: ERRORE"

def cerca_su_google(query):
    try:
        risultati = list(search(query, num_results=1))
        return f"Ho trovato: {risultati[0]}" if risultati else "Nessun risultato."
    except Exception as e:
        return f"Errore ricerca: {str(e)}"

async def handler(websocket):
    logger.info("Connessione stabilita.")
    
    async def inviatore():
        while True:
            try:
                cpu = psutil.cpu_percent(interval=1)
                mem = psutil.virtual_memory().percent
                
                domanda = "Sistema ok."
                if cpu > 85:
                    domanda = "Carico elevato: vuoi eseguire pulizia?"
                elif random.random() < 0.05:
                    domanda = random.choice(domande_di_apprendimento)
                
                dati = {
                    "sicurezza": "ALLERTA" if cpu > 85 else "NORMALE",
                    "visione": scansiona_sicura(),
                    "monitoraggio": {"cpu": cpu, "ram": mem},
                    "domanda": domanda
                }
                await websocket.send(json.dumps(dati))
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Errore invio: {e}")
                break

    async def ricevitore():
        async for message in websocket:
            try:
                comando = json.loads(message)
                risposta = ""
                
                # 1. Comando: Cosa sai fare
                if "cosa sai fare" in str(comando).lower():
                    risposta = ("Le mie funzioni attive sono: monitoraggio CPU e RAM in tempo reale, "
                                "analisi immagini tramite OCR, ricerche rapide su Google, "
                                "pulizia automatica dei file temporanei e archiviazione "
                                "intelligente di informazioni nel mio nucleo di memoria.")
                
                # 2. Azione: Pulizia
                elif comando.get("azione") == "pulisci" or "pulisci" in str(comando).lower():
                    risposta = fabbrica.pulisci_file_temporanei()
                
                # 3. Azione: Analisi Immagini
                elif "file_caricato" in comando:
                    percorso = comando["file_caricato"]
                    risposta = visione_ai.analizza_file(percorso)
                
                # 4. Azione: Conversazione e Memoria
                elif "comando_testuale" in comando:
                    testo = comando["comando_testuale"].lower()
                    if "cerca" in testo:
                        risposta = cerca_su_google(testo.replace("cerca", "").strip())
                    else:
                        risposta = memoria.salva_informazione(comando["comando_testuale"])
                        risposta = f"Ho registrato: {comando['comando_testuale']}. Grazie per l'informazione."
                
                if risposta:
                    await websocket.send(json.dumps({"feedback": str(risposta)}))
            except Exception as e:
                logger.error(f"Errore comando: {e}")

    aw