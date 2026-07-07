import asyncio
import logging
import psutil

# Configurazione del logger per vedere cosa fa l'agente nel terminale
logger = logging.getLogger("AgenteProattivo")

async def avvia_battito():
    """
    Questo è il battito cardiaco dell'IA. 
    Gira in background 24/7 e monitora le risorse del sistema.
    """
    logger.info("Agente Proattivo: Battito cardiaco avviato.")
    
    while True:
        try:
            # Monitoraggio in tempo reale del carico CPU
            cpu_load = psutil.cpu_percent(interval=1)
            
            # Logica proattiva reale: 
            # Se la CPU supera il 90%, l'agente lo rileva e logga un'allerta
            if cpu_load > 90:
                logger.warning(f"ALLERTA: Carico CPU elevato rilevato: {cpu_load}%")
                # Qui potrai aggiungere azioni reali (es. chiusura processi)
            
            # Pausa di 60 secondi prima del prossimo battito
            await asyncio.sleep(60)
            
        except Exception as e:
            logger.error(f"Errore nel battito cardiaco: {e}")
            await asyncio.sleep(10)