import psutil
import asyncio
import json
import websockets
import time

SERVER_URL = "ws://localhost:8000/ws/windows"

async def monitora_sistema():
    print("[SICUREZZA] Avvio monitoraggio processi attivo...")
    async with websockets.connect(SERVER_URL) as ws:
        while True:
            # Esempio: monitora l'uso della CPU e processi sospetti
            cpu_usage = psutil.cpu_percent(interval=1)
            processi = [p.info['name'] for p in psutil.process_iter(['name'])]
            
            # Se la CPU è troppo alta o c'è un processo "strano", avvisa il server
            if cpu_usage > 90:
                avviso = {
                    "mittente": "windows",
                    "tipo": "avviso_sicurezza",
                    "contenuto": f"Attenzione: Uso CPU critico al {cpu_usage}%!"
                }
                await ws.send(json.dumps(avviso))
            
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(monitora_sistema())