# server.py
import asyncio
import json
import os
import sys
import logging
import traceback
from typing import Optional

# --- CONFIGURAZIONE LOGGING PROFESSIONALE (Apprendimento e Diagnostica 24/7) ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SIA_SERVER] - %(levelname)s - %(message)s')
logger = logging.getLogger("SIA_Server")

# Assicura che il percorso del progetto sia disponibile per l'importazione
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) if os.path.basename(current_dir) != "Progetto_IA_Personale" else current_dir

if project_root not in sys.path:
    sys.path.insert(0, project_root)
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Importa il cervello dall'Area Core con sistema di fallback anti-crash
try:
    import Area_Core.brain_logic as brain_logic_module
    logger.info("Modulo Area_Core.brain_logic importato standard.")
except ImportError:
    import importlib.util
    logger.warning("Importazione standard fallita. Tentativo di fallback in corso...")

    brain_logic_candidates = [
        os.path.join(project_root, "Area_Core", "brain_logic.py"),
        os.path.join(current_dir, "Area_Core", "brain_logic.py"),
        os.path.join(os.getcwd(), "Area_Core", "brain_logic.py")
    ]
    brain_logic_path = next((path for path in brain_logic_candidates if os.path.exists(path)), None)

    if brain_logic_path is None:
        logger.error("ERRORE CRITICO: File brain_logic.py non trovato.")
        # Se manca il file logico, creiamo un cervello "finto" per non spegnere il server
        class MockBrain:
            async def monitoraggio_loop(self, websocket):
                while True:
                    await asyncio.sleep(60)
            async def process_message(self, message):
                return {"azione": "ERRORE", "testo": "Cervello (brain_logic.py) non collegato."}
            async def process_visual_data(self, message):
                return {"azione": "ERRORE", "testo": "Modulo visione non collegato."}
            async def impara_da_errore(self, errore_log):
                pass # Stub per evitare crash se il metodo manca
        
        class MockModule:
            BrainCore = MockBrain
        
        brain_logic_module = MockModule
        logger.warning("Sto usando un modulo di emergenza per mantenere il server acceso.")
    else:
        spec = importlib.util.spec_from_file_location("Area_Core.brain_logic", brain_logic_path)
        brain_logic_module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = brain_logic_module
        spec.loader.exec_module(brain_logic_module)
        logger.info("Fallback importazione completato con successo.")

logger.info("IL FILE È PARTITO!")

# Gestione robusta dell'importazione di websockets
try:
    import websockets
except ImportError:
    logger.error("[ERRORE]: Libreria 'websockets' mancante. Esegui: pip install websockets")
    raise ImportError("Libreria 'websockets' mancante. Impossibile avviare il motore di rete.")

async def handler(websocket, *args, **kwargs):
    """Gestore principale della connessione WebSocket per elaborazione continua."""
    client_address = websocket.remote_address if hasattr(websocket, 'remote_address') else "Client Sconosciuto"
    logger.info(f"Connessione stabilita con il client: {client_address}")
    
    # Inizializza il cervello per questa sessione
    try:
        brain = brain_logic_module.BrainCore()
    except Exception as e:
        logger.error(f"Errore di avvio del BrainCore: {e}")
        return
    
    # Avvia il loop in background per il monitoraggio e la sorveglianza autonoma 24/7
    monitor_task = asyncio.create_task(brain.monitoraggio_loop(websocket))

    try:
        async for message in websocket:
            # --- 1. RICEZIONE DATI VISIVI / FILE ---
            if isinstance(message, bytes):
                logger.info(f"Ricevuto file binario di {len(message)} byte. Avvio assimilazione dati 24/7...")
                if hasattr(brain, 'process_visual_data'):
                    # Qui il sistema legge il file (es. estrarre turni di lavoro da una foto per impostare sveglie)
                    response = await brain.process_visual_data(message)
                else:
                    response = {"azione": "ERRORE", "testo": "Metodo process_visual_data mancante. Impossibile assimilare il file."}
            
            # --- 2. RICEZIONE TESTO E COMANDI ---
            else:
                logger.info("Interazione di testo ricevuta dal client.")
                response = await brain.process_message(message)
            
            # --- 3. INVIO RISPOSTA E GENERAZIONE FILE ---
            if response:
                if isinstance(response, dict):
                    # Gestione avanzata: Se l'IA ha generato un file (es. un'immagine creata) da inviare al client
                    if response.get("azione") == "INVIA_FILE_GENERATO" and "dati_binari" in response:
                        logger.info("L'IA ha creato un file. Avvio del trasferimento al client...")
                        # Invia prima i byte puri del file creato
                        await websocket.send(response["dati_binari"])
                        # Prepara un payload leggero di conferma per l'interfaccia utente
                        payload = json.dumps({
                            "azione": "FILE_RICEVUTO", 
                            "testo": response.get("testo", "Ecco il file che ho generato per te.")
                        }, ensure_ascii=False)
                    else:
                        # Risposta testuale/comando standard
                        payload = json.dumps(response, ensure_ascii=False)
                else:
                    payload = str(response)
                
                await websocket.send(payload)
                logger.info("Dati inviati al client con successo.")
                
    except websockets.exceptions.ConnectionClosed as e:
        logger.warning(f"Client disconnesso regolarmente (Codice: {e.code}).")
    except Exception as e:
        # --- 4. AUTO-APPRENDIMENTO DAGLI ERRORI ---
        errore_dettagliato = traceback.format_exc()
        logger.error(f"Errore critico durante l'elaborazione. Avvio routine di auto-analisi:\n{errore_dettagliato}")
        if hasattr(brain, 'impara_da_errore'):
            # Invia l'errore al cervello in modo che possa registrarlo, capirlo e non ripeterlo
            await brain.impara_da_errore(errore_dettagliato)
    finally:
        # Quando il client chiude l'app, fermiamo il task in background per liberare la memoria
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass
        logger.info("Sessione chiusa e risorse liberate.")

async def main():
    """Funzione principale che avvia il server, richiamabile anche da moduli esterni."""
    host = "0.0.0.0"
    port = 8080
    logger.info(f"SIA - Sistema Integrato Autonomo Online su ws://{host}:{port}")
    
    try:
        # max_size a 500MB per permettere transito di video pesanti, archivi o file molto grossi
        async with websockets.serve(
            handler, 
            host, 
            port, 
            ping_interval=20, 
            ping_timeout=20, 
            max_size=524288000
        ):
            await asyncio.Future()
    except OSError as e:
        logger.error(f"ERRORE AVVIO: Porta {port} bloccata. Controlla di non avere altri server aperti. {e}")
    except Exception as e:
        logger.error(f"Errore fatale del server: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nCHIUSURA: SIA terminato manualmente. Arrivederci!")