import asyncio
import websockets
import json
import psutil

# Questa funzione gestisce ogni singola connessione che arriva dal frontend
async def handler(websocket, path):
    print("Connessione stabilita con il frontend Flutter!")
    try:
        while True:
            # Rileva l'uso della CPU del sistema
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Crea il messaggio JSON completo
            messaggio = json.dumps({
                "stato": "attivo",
                "cpu": f"{cpu_usage}%",
                "messaggio": "Monitoraggio in tempo reale"
            })
            
            # Invia il messaggio al client collegato
            await websocket.send(messaggio)
            
            # Attende un secondo prima del prossimo ciclo
            await asyncio.sleep(1)
    except Exception as e:
        print(f"Connessione chiusa o errore durante l'invio: {e}")

# Avvia il server WebSocket sulla porta 8080 (fissa)
print("Avvio del server WebSocket in corso...")
print("Server in attesa di connessioni su ws://localhost:8080...")

start_server = websockets.serve(handler, "localhost", 8080)

# Esecuzione del server in un loop infinito
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()