import asyncio
import websockets
import json
import psutil

# Funzione gestore: ogni volta che un client (Flutter) si connette, questa parte viene eseguita
async def handler(websocket, path):
    print("Connessione stabilita con il frontend Flutter!")
    try:
        while True:
            # Rilevamento dati hardware
            cpu_usage = psutil.cpu_percent(interval=1)
            
            # Creazione del pacchetto dati completo
            dati = {
                "stato": "attivo",
                "cpu": cpu_usage,
                "messaggio": "Monitoraggio sistema in tempo reale"
            }
            
            # Invio dei dati come stringa JSON
            await websocket.send(json.dumps(dati))
            
            # Pausa di 1 secondo come richiesto per il monitoraggio costante
            await asyncio.sleep(1)
            
    except websockets.exceptions.ConnectionClosed:
        print("Il client Flutter si è disconnesso.")
    except Exception as e:
        print(f"Errore durante la comunicazione: {e}")

# Configurazione del server WebSocket
# Utilizziamo 'localhost' e la porta 8080 per garantire la stabilità
print("Avvio del server WebSocket...")
start_server = websockets.serve(handler, "localhost", 8080)

print("Server in ascolto su ws://localhost:8080. Non chiudere questa finestra.")

# Avvio del loop degli eventi
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()