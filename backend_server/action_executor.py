import time
import json
import os
import subprocess

# Percorso del file che il Cervello aggiorna con le decisioni
COMMAND_FILE = "pending_commands.json"

def execute_action(command_data):
    """
    Interpreta il JSON inviato dal Cervello ed esegue l'azione su Windows
    """
    action = command_data.get("azione")
    details = command_data.get("dettagli", {})

    print(f"Esecuzione comando: {action}")

    if action == "IMPOSTA_SVEGLIA":
        # Esempio: Apre l'app Sveglia di Windows (o crea un file di log)
        ora = details.get("ora", "08:00")
        print(f"Impostando sveglia alle {ora}...")
        # Comando per Windows per aprire l'app Sveglia (esempio)
        os.system("start ms-clock:")
        
    elif action == "CREA_PROMEMORIA":
        # Scrive su un file di testo il promemoria
        with open("miei_promemoria.txt", "a") as f:
            f.write(f"\n- {details.get('descrizione', 'Nessuna descrizione')}")
        print("Promemoria salvato su file.")

    elif action == "APRI_APP":
        app_name = details.get("nome", "notepad")
        subprocess.Popen(app_name)

def monitor_commands():
    """
    Loop infinito che controlla se ci sono nuovi ordini dal Cervello
    """
    print("Esecutore attivo. In attesa di ordini...")
    last_processed = None
    
    while True:
        if os.path.exists(COMMAND_FILE):
            with open(COMMAND_FILE, "r") as f:
                try:
                    data = json.load(f)
                    # Controlla se è un nuovo comando non ancora elaborato
                    if data != last_processed:
                        execute_action(data)
                        last_processed = data
                except:
                    pass
        time.sleep(2) # Controlla ogni 2 secondi

if __name__ == "__main__":
    monitor_commands()