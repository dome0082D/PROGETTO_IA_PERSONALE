import asyncio
import logging
import psutil

logger = logging.getLogger("AgenteProattivo")

async def battito_cardiaco(guardiano_istanza):
    """Il ciclo costante che analizza il sistema in background."""
    while True:
        cpu = psutil.cpu_percent()
        # Logica di auto-apprendimento: se rileva anomalia, usa la memoria
        if cpu > 95:
            logger.warning("ANOMALIA RILEVATA dal battito cardiaco!")
            guardiano_istanza.memoria.salva_evento("ANOMALIA_CPU", f"Uso al {cpu}%")
        
        await asyncio.sleep(5) # Analisi ogni 5 secondi