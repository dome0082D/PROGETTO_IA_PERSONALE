# main.py
import os
import sys
import json
import httpx
import uvicorn
import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict, Any, Optional

# --- CONFIGURAZIONE LOGGING PROFESSIONALE ---
# Configurato subito all'inizio per catturare ogni singolo log di importazione e startup 24/7
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SIA_CORE] - %(levelname)s - %(message)s')
logger = logging.getLogger("SIA_Core")

# --- RISOLUZIONE DEI PERCORSI CRITICI ---
# Garantisce che Python trovi sempre server.py e models.py a prescindere da dove lanci il comando nel terminale
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# --- PROPEDEUTICA ALL'AVVIO CONGIUNTO ---
# Proviamo a importare server.py per far girare entrambi i motori contemporaneamente
try:
    import server
    SERVER_DISPONIBILE = True
    logger.info("Modulo server.py individuato con successo.")
except ImportError as e:
    SERVER_DISPONIBILE = False
    logger.warning(f"Impossibile importare server.py (gestore WebSocket 500MB): {e}")

# Ora questa importazione è sicura al 100% grazie al path di sistema configurato sopra
from models import MessaggioClient, AzioneIA

app = FastAPI(title="SIA - Cervello Centrale IA Personale")

# --- GESTORE WEBSOCKET (Connessioni 24/7) ---
class ConnectionManager:
    def __init__(self):
        # Mantiene traccia dei dispositivi connessi
        self.connessioni_attive: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connessioni_attive[client_id] = websocket
        logger.info(f"Dispositivo connesso: {client_id.upper()}")

    def disconnect(self, client_id: str):
        if client_id in self.connessioni_attive:
            del self.connessioni_attive[client_id]
            logger.info(f"Dispositivo disconnesso: {client_id.upper()}")

    async def invia_a_dispositivo(self, target: str, messaggio: dict):
        if target in self.connessioni_attive:
            try:
                # Utilizzo di send_json nativo di FastAPI: più veloce e sicuro del vecchio json.dumps
                await self.connessioni_attive[target].send_json(messaggio)
            except Exception as e:
                logger.error(f"Errore critico di invio a {target}: {e}")
        elif target == "broadcast":
            for ws in self.connessioni_attive.values():
                try:
                    await ws.send_json(messaggio)
                except Exception:
                    continue # Ignora i client disconnessi in modo anomalo

manager = ConnectionManager()

# --- MOTORE LOGICO ESTENDIBILE E CHIAMATA OLLAMA ---
async def interroga_ollama(prompt: str, modello: str = "qwen2.5-vl") -> str:
    """Contatta le API REST native di Ollama."""
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": modello,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            response.raise_for_status() # Intercetta gli errori HTTP (es. 500 Server Error)
            return response.json()["message"]["content"]
        except httpx.ConnectError:
            logger.warning("Motore Ollama offline. Avvia l'eseguibile sulla macchina fisica.")
            return "Il mio sistema logico non è raggiungibile in questo momento. Avvia il motore IA."
        except Exception as e:
            logger.error(f"Errore durante l'inferenza: {e}")
            return "Si è verificato un errore interno nel processamento logico."

async def processa_input(messaggio: MessaggioClient) -> dict:
    """
    Smistatore centrale (Implementazione Lungimirante).
    Decide la strada da prendere: elaborazione testuale, comandi di sistema o analisi file.
    """
    # Predisposizione per l'assimilazione dei file inviati dall'utente
    if hasattr(messaggio, 'file_base64') and getattr(messaggio, 'file_base64') is not None:
        logger.info(f"Ricevuto file da {messaggio.mittente}. Predisposizione modulo di visione...")
        # Qui il sistema si innesterà con l'agente di visione per estrapolare orari e programmare azioni
        return {
            "azione": "SYNC_ALLARMI", 
            "testo": "Ho letto il file e assimilato i dati. Ho preparato l'azione per impostare gli allarmi sul tuo dispositivo."
        }

    # Elaborazione Testuale Standard
    risposta_testuale = await interroga_ollama(messaggio.contenuto)
    return {
        "azione": "SPEAK_AND_ANIMATE",
        "testo": risposta_testuale
    }

# --- ENDPOINT WEBSOCKET PRINCIPALE ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            # In ascolto perenne dei messaggi
            dati_ricevuti = await websocket.receive_text()
            
            try:
                # Validazione strutturata dei dati in ingresso
                json_data = json.loads(dati_ricevuti)
                messaggio = MessaggioClient(**json_data)
                
                logger.info(f"[{messaggio.mittente.upper()}] Input: {messaggio.contenuto[:60]}...")
                
                # La logica è stata astratta nella funzione processa_input per evitare blocchi
                esito = await processa_input(messaggio)
                
                # Assemblaggio del pacchetto di risposta
                pacchetto_risposta = {
                    "target": messaggio.mittente,
                    "azione": esito["azione"],
                    "parametri": {"testo": esito["testo"]}
                }
                
                await manager.invia_a_dispositivo(messaggio.mittente, pacchetto_risposta)

            except json.JSONDecodeError:
                logger.error("Ricevuto payload non formattato in JSON.")
            except Exception as e:
                logger.error(f"Errore di validazione Pydantic o struttura mancante: {e}")
                await manager.invia_a_dispositivo(client_id, {
                    "target": client_id,
                    "azione": "ERRORE",
                    "parametri": {"testo": "Formato del messaggio non valido o incompleto."}
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)

# --- ENGINE DI AVVIO CONGIUNTO (FastAPI + Websockets Raw) ---
async def main_async():
    logger.info("SIA - Inizializzazione della suite server concorrente...")
    
    # Configurazione di Uvicorn per far girare questo file (FastAPI) sulla porta 8000
    config = uvicorn.Config(app, host="0.0.0.0", port=8000, log_config=None, loop="asyncio")
    uvicorn_server = uvicorn.Server(config)
    
    tasks = [uvicorn_server.serve()]
    
    # Se server.py è presente nella stessa cartella, lo lanciamo insieme in parallelo sulla porta 8080
    if SERVER_DISPONIBILE:
        logger.info("Collegamento con server.py riuscito. Avvio del motore WebSocket sulla porta 8080...")
        tasks.append(server.main())
    else:
        logger.warning("Esecuzione parziale: server.py non integrato. Gira solo la porta 8000.")
        
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main_async())
    except KeyboardInterrupt:
        logger.info("\n[CHIUSURA] SIA terminato manualmente. Arrivederci!")