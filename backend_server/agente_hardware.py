import psutil
import os

def analizza_sistema():
    # Analisi risorse
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory().percent
    disco = psutil.disk_usage('C:\\').percent
    
    report = f"Stato Sistema: CPU {cpu}%, RAM {ram}%, Disco {disco}%."
    
    # Azioni proattive
    avvisi = []
    if ram > 85:
        avvisi.append("RAM molto alta. Vuoi che chiuda i processi non necessari?")
    if disco > 90:
        avvisi.append("Disco quasi pieno. Vuoi pulire i file temporanei?")
        
    return report, avvisi

def esegui_pulizia():
    # Comando di esempio per pulire i temporanei di Windows
    os.system("del /q /s /f %temp%\\*")
    return "Pulizia file temporanei completata."