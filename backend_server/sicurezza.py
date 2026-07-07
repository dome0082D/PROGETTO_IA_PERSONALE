import asyncio
import websockets
import json
import psutil
import time

# Configurazione URL del server (Flutter app deve essere in ascolto qui)
SERVER_URL = "ws://localhost:8000/ws/windows"

async def monitora_sistema():
    print("[SISTEMA] Avvio monitoraggio processi attivo...")
    
    while True:
        try:
            # Tenta di connettersi al server Flutter
            async with websockets.connect(SERVER_URL) as ws:
                print("Connessione stabilita con successo!")
                
                while True:
                    # Rilevamento dati
                    cpu_usage = psutil.cpu_percent(interval=1)
                    processi = [p.info['name'] for p in psutil.process_iter(['name'])]
                    
                    # Logica di avviso
                    if cpu_usage > 90:
                        avviso = {
                            "mittente": "windows",
                            "tipo": "avviso_sicurezza",
                            "contenuto": f"Attenzione: Uso CPU critico al {cpu_usage}%"
                        }
                        await ws.send(json.dumps(avviso))
                        print(f"Inviato avviso: {avviso['contenuto']}")
                    
                    await asyncio.sleep(5)
                    
        except (websockets.exceptions.ConnectionClosed, ConnectionRefusedError):
            print("Server non trovato. Riprovo la connessione tra 5 secondi...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"Errore imprevisto: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    try:
        asyncio.run(monitora_sistema())
    except KeyboardInterrupt:
        print("Monitoraggio interrotto dall'utente.")