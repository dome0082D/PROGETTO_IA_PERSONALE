import psutil
import os

def analizza_sistema():
    """Analizza lo stato delle risorse hardware e genera avvisi proattivi."""
    try:
        # Analisi in tempo reale
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disco = psutil.disk_usage('C:\\').percent
        
        report = f"Stato Sistema: CPU {cpu}%, RAM {ram}%, Disco {disco}%."
        
        # Logica di monitoraggio proattivo
        avvisi = []
        if ram > 85:
            avvisi.append("RAM molto alta. Vuoi che chiuda i processi non necessari?")
        if disco > 90:
            avvisi.append("Disco quasi pieno. Vuoi pulire i file temporanei?")
            
        return report, avvisi
    
    except Exception as e:
        print(f"[ERRORE AGENTE HARDWARE]: {e}")
        return "Errore nella lettura dei sensori hardware.", []

def get_cpu_usage():
    """Funzione specifica per il monitoraggio veloce richiesto dal loop."""
    try:
        return psutil.cpu_percent(interval=0.1)
    except:
        return 0.0

def esegui_pulizia():
    """Esegue la rimozione dei file temporanei di sistema."""
    try:
        # Il comando Windows per pulire i temp
        os.system("del /q /s /f %temp%\\*")
        return "Pulizia file temporanei completata con successo."
    except Exception as e:
        return f"Errore durante la pulizia: {e}"