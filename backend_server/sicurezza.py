import asyncio
import websockets
import json
import psutil

async def handler(websocket, path):
    print("Connessione stabilita con Flutter!")
    try:
        while True:
            cpu = psutil.cpu_percent(interval=1)
            dati = {"cpu": f"{cpu}%"}
            await websocket.send(json.dumps(dati))
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Errore: {e}")

# Forza il server a stare su 127.0.0.1 porta 8080
start_server = websockets.serve(handler, "127.0.0.1", 8080)

print("Server attivo su ws://127.0.0.1:8080")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()