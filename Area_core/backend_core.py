# Area_Core/backend_core.py
import os
import json
import logging
from datetime import datetime

# 1. Calcolo Dinamico dei Percorsi (Lungimiranza Strutturale)
# Questo garantisce che il sistema trovi sempre i file, ovunque tu metta la cartella principale.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CORE_DIR = os.path.join(BASE_DIR, "Area_Core")
AGENTI_DIR = os.path.join(BASE_DIR, "Area_Agenti")
MEDIA_DIR = os.path.join(BASE_DIR, "Area_Media") 

# 2. Configurazione Centralizzata
CONFIG = {
    "SISTEMA": "SIA",
    "VERSIONE": "2.1.0",
    "HOST": "0.0.0.0",
    "PORTA": 8080,
    "MODULO_LLM": "llama3",
    "VOCE_TTS": "it-IT-ChiaraNeural",
    "DEBUG_MODE": True,
    
    # Gestione Memoria
    "MEMORIA_FILE": os.path.join(CORE_DIR, "memoria_personale.json"),
    
    # Preparazione per assimilazione e creazione file
    "PERCORSO_INPUT_FILE": os.path.join(MEDIA_DIR, "input"),
    "PERCORSO_OUTPUT_FILE": os.path.join(MEDIA_DIR, "output"),
}

# Assicuriamoci che le cartelle essenziali esistano prima ancora che il server parta
os.makedirs(CONFIG["PERCORSO_INPUT_FILE"], exist_ok=True)
os.makedirs(CONFIG["PERCORSO_OUTPUT_FILE"], exist_ok=True)

# 3. Setup Logging (Tracciamento errori per auto-apprendimento)
logging.basicConfig(
    level=logging.DEBUG if CONFIG["DEBUG_MODE"] else logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, "sistema.log"), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SIA_Controller")

# --- NUOVA INTEGRAZIONE: CONSAPEVOLEZZA TEMPORALE ---
def ottieni_contesto_temporale():
    """
    Restituisce l'ora e la data esatta del sistema operativo per iniettarla nell'IA.
    Questo risolve il problema dei placeholder [Inserire l'ora].
    """
    ora_esatta = datetime.now().strftime("%H:%M")
    data_esatta = datetime.now().strftime("%d/%m/%Y")
    giorno_settimana = datetime.now().strftime("%A")
    
    # Rendi il giorno in italiano (se il sistema operativo restituisce inglese)
    giorni_it = {
        "Monday": "Lunedì", "Tuesday": "Martedì", "Wednesday": "Mercoledì",
        "Thursday": "Giovedì", "Friday": "Venerdì", "Saturday": "Sabato", "Sunday": "Domenica"
    }
    giorno_it = giorni_it.get(giorno_settimana, giorno_settimana)

    return f"ISTRUZIONE DI SISTEMA: Ora attuale: {ora_esatta}. Data di oggi: {data_esatta} ({giorno_it}). Se ti viene chiesto il tempo, rispondi sempre e solo in modo colloquiale usando questi dati reali. Non usare mai placeholder o parentesi quadre."

# 4. Strumenti di Utility Globale
def carica_memoria():
    """Utility comune per leggere la memoria. Gestisce i percorsi assoluti in sicurezza."""
    if not os.path.exists(CONFIG["MEMORIA_FILE"]):
        return []
    try:
        with open(CONFIG["MEMORIA_FILE"], "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except Exception as e:
        logger.error(f"Errore critico nella lettura della memoria: {e}")
        return []

def salva_memoria(memoria):
    """Utility comune per salvare la memoria."""
    try:
        with open(CONFIG["MEMORIA_FILE"], "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Errore critico nella scrittura della memoria: {e}")

# 5. Stato del Sistema (Per monitoraggio centrale in tempo reale)
SYSTEM_STATE = {
    "server_online": True,
    "agenti_attivi": [],
    "file_in_elaborazione": 0 
}