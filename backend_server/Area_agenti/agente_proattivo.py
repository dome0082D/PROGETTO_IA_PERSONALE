import asyncio
import logging
import psutil

# Configurazione del logger per mostrare i dettagli nel terminale di VS Code
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AgenteProattivo")

# Inizializzazione non bloccante del contatore CPU di sistema
psutil.cpu_percent(interval=None)

def ottieni_processi_pesanti():
    """
    Scansiona i processi attivi sul sistema e isola i 3 colpevoli 
    che stanno consumando più risorse (CPU e RAM).
    """
    processi = []
    # Recuperiamo solo le metriche essenziali per massimizzare la velocità
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            info = proc.info
            # Evitiamo valori None inserendo 0.0 come fallback sicuro
            if info.get('cpu_percent') is None:
                info['cpu_percent'] = 0.0
            if info.get('memory_percent') is None:
                info['memory_percent'] = 0.0
            processi.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
            
    # Ordina i processi per consumo decrescente
    top_cpu = sorted(processi, key=lambda p: p.get('cpu_percent', 0.0), reverse=True)[:3]
    top_ram = sorted(processi, key=lambda p: p.get('memory_percent', 0.0), reverse=True)[:3]
    
    return top_cpu, top_ram

async def avvia_battito():
    """
    Il battito cardiaco di SIA. Gira in background 24/7.
    Monitora le risorse in modo proattivo senza mai bloccare il server principale.
    """
    logger.info("Agente Proattivo: Battito cardiaco avviato con successo.")
    
    while True:
        try:
            # Lettura istantanea dell'utilizzo attuale
            cpu_load = psutil.cpu_percent(interval=None)
            ram_load = psutil.virtual_memory().percent
            
            # Soglie di allerta proattiva per salvaguardare il sistema
            if cpu_load > 85 or ram_load > 90:
                logger.warning(f"[SIA ALLERTA RISORSE]: CPU al {cpu_load}% | RAM al {ram_load}%")
                
                # Eseguiamo la pesante scansione dei processi in un thread separato
                # per non bloccare l'event loop di asyncio
                top_cpu, top_ram = await asyncio.to_thread(ottieni_processi_pesanti)
                
                if cpu_load > 85 and top_cpu:
                    logger.warning("Rilevato picco CPU! Processi più pesanti attivi:")
                    for p in top_cpu:
                        logger.warning(f"  -> {p['name']} (PID: {p['pid']}) consuma il {p['cpu_percent']}% di CPU")
                        
                if ram_load > 90 and top_ram:
                    logger.warning("Rilevato picco RAM! Processi più pesanti attivi:")
                    for p in top_ram:
                        logger.warning(f"  -> {p['name']} (PID: {p['pid']}) consuma il {p['memory_percent']:.1f}% di RAM")
            
            # Controllo regolare ogni 60 secondi
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Errore nel battito cardiaco: {e}")
            await asyncio.sleep(10)


# --- INTERFACCIA PER IL NUOVO LOADER MODULARE ---
def esegui(comando=""):
    """
    Interfaccia standard. Permette a SIA di dialogare con l'agente su richiesta.
    """
    cmd = comando.lower().strip()
    
    if "risorse" in cmd or "stato" in cmd or "hardware" in cmd:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent
        return f"SIA Proattiva: CPU attuale al {cpu}% e RAM al {ram}%."
        
    if "processi" in cmd or "pesanti" in cmd or "rallenta" in cmd:
        top_cpu, top_ram = ottieni_processi_pesanti()
        risposta = "Ecco la diagnostica dei processi attivi:\n\n"
        risposta += "🔥 Consumo CPU maggiore:\n"
        for p in top_cpu:
            risposta += f"- {p['name']} (PID: {p['pid']}) -> {p['cpu_percent']}%\n"
        risposta += "\n💾 Consumo RAM maggiore:\n"
        for p in top_ram:
            risposta += f"- {p['name']} (PID: {p['pid']}) -> {p['memory_percent']:.1f}%\n"
        return risposta
        
    return "Agente Proattivo operativo in background e vigile sul sistema."