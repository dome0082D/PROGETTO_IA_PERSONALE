import asyncio
import websockets
import json
import psutil

# Indirizzo del server
SERVER_URL = "ws://localhost:8000/ws/windows"

async def monitora_sistema():
    print("[SISTEMA] Avvio monitoraggio processi attivo...")
    while True:
        try:
            # Tenta la connessione al server
            async with websockets.connect(SERVER_URL) as ws:
                print("Connessione stabilita con successo!")
                while True:
                    # Monitoraggio CPU
                    cpu_usage = psutil.cpu_percent(interval=1)
                    # Preparazione messaggio
                    msg = json.dumps({
                        "mittente": "windows",
                        "tipo": "stato_sistema",
                        "cpu": cpu_usage
                    })
                    await ws.send(msg)
                    await asyncio.sleep(1)
        except Exception:
            # Se il server non è pronto, attende e riprova
            print("Server non trovato, riprovo tra 5 secondi...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitora_sistema())