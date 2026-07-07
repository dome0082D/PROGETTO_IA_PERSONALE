import subprocess
import os

def disinstalla_programma(nome_processo):
    """Chiude forzatamente un processo che rallenta il PC."""
    try:
        subprocess.run(f"taskkill /F /IM {nome_processo}.exe", shell=True)
        return f"Processo {nome_processo} terminato con successo."
    except Exception as e:
        return f"Errore: {e}"