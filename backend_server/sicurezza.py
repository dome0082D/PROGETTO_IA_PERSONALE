import asyncio
import websockets
import json
import psutil
import time

# Configurazione
SERVER_URL = "ws://localhost:8080/ws/windows"

async def monitora_sistema():
    print("[SISTEMA] Avvio monitoraggio processi attivo...")
    while True:
        try:
            # Tenta la connessione al server (l'app Flutter)
            async with websockets.connect(SERVER_URL) as ws:
                print("Connessione stabilita con successo!")
                while True:
                    # Logica di monitoraggio CPU
                    cpu_usage = psutil.cpu_percent(interval=1)
                    if cpu_usage > 90:
                        avviso = {
                            "mittente": "windows",
                            "tipo": "avviso_sicurezza",
                            "contenuto": f"Attenzione: Uso CPU critico al {cpu_usage}%!"
                        }
                        await ws.send(json.dumps(avviso))
                    await asyncio.sleep(1)
        except Exception as e:
            print(f"Server non trovato, riprovo tra 5 secondi... ({e})")
            await asyncio.sleep(5) # Attesa prima di tentare la riconnessione

if __name__ == "__main__":
    asyncio.run(monitora_sistema())