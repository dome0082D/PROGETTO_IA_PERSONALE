import json
import os
import datetime

MEMORIA_FILE = "memoria_io.json"

def salva_informazione(input_utente):
    """Archivia un'informazione nel database locale dell'IA."""
    dati = {}
    
    # Carica la memoria esistente se c'è
    if os.path.exists(MEMORIA_FILE):
        with open(MEMORIA_FILE, "r", encoding="utf-8") as f:
            try:
                dati = json.load(f)
            except:
                dati = {}
    
    # Crea una nuova entrata con timestamp
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    dati[timestamp] = input_utente
    
    # Salva il file
    with open(MEMORIA_FILE, "w", encoding="utf-8") as f:
        json.dump(dati, f, indent=4, ensure_ascii=False)
    
    return "Informazione archiviata nel nucleo centrale."