import json
import httpx
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Dict
from models import MessaggioClient, AzioneIA

app = FastAPI(title="Cervello Centrale IA Personale")

# --- GESTORE WEBSOCKET (Connessioni 24/7) ---
class ConnectionManager:
    def __init__(self):
        # Mantiene traccia dei dispositivi connessi: es. {"android": websocket, "windows": websocket}
        self.connessioni_attive: Dict[str, WebSocket] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.connessioni_attive[client_id] = websocket
        print(f"[SISTEMA] Dispositivo connesso: {client_id.upper()}")

    def disconnect(self, client_id: str):
        if client_id in self.connessioni_attive:
            del self.connessioni_attive[client_id]
            print(f"[SISTEMA] Dispositivo disconnesso: {client_id.upper()}")

    async def invia_a_dispositivo(self, target: str, messaggio: dict):
        if target in self.connessioni_attive:
            await self.connessioni_attive[target].send_text(json.dumps(messaggio))
        elif target == "broadcast":
            for ws in self.connessioni_attive.values():
                await ws.send_text(json.dumps(messaggio))

manager = ConnectionManager()

# --- CHIAMATA REALE AL MOTORE IA (OLLAMA LOCALE) ---
async def interroga_ollama(prompt: str, modello: str = "qwen2.5-vl") -> str:
    """
    Contatta le API REST native di Ollama sul nuovo computer per elaborare la risposta.
    """
    url = "http://localhost:11434/api/chat"
    payload = {
        "model": modello,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=60.0)
            if response.status_code == 200:
                dati = response.json()
                return dati["message"]["content"]
            return "Errore nella comunicazione con Ollama."
        except Exception as e:
            # Utile durante lo sviluppo o se Ollama non è ancora avviato sul PC attuale
            print(f"[ATTENZIONE] Motore Ollama non raggiungibile: {e}")
            return "Motore IA locale al momento offline. Avviare Ollama sulla macchina fisica."

# --- ENDPOINT WEBSOCKET PRINCIPALE ---
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(client_id, websocket)
    try:
        while True:
            # Rimaneggia in ascolto perenne dei messaggi da Windows o Android
            dati_ricevuti = await websocket.receive_text()
            
            try:
                # Valida i dati in ingresso con Pydantic
                json_data = json.loads(dati_ricevuti)
                messaggio = MessaggioClient(**json_data)
                
                print(f"[{messaggio.mittente.upper()}] Ricevuto: {messaggio.contenuto}")
                
                # Interroga l'IA sul messaggio ricevuto
                risposta_ia = await interroga_ollama(messaggio.contenuto)
                
                # Invia la risposta all'interfaccia (es. all'equalizzatore grafico di Android)
                pacchetto_risposta = {
                    "target": messaggio.mittente,
                    "azione": "SPEAK_AND_ANIMATE",
                    "parametri": {"testo": risposta_ia}
                }
                await manager.invia_a_dispositivo(messaggio.mittente, pacchetto_risposta)

            except Exception as e:
                print(f"[ERRORE DI FORMATO] {e}")

    except WebSocketDisconnect:
        manager.disconnect(client_id)

# Avvio del server
if __name__ == "__main__":
    import uvicorn
    # Gira sulla porta 8000 ed è visibile a tutti i dispositivi nella rete locale (0.0.0.0)
    uvicorn.run(app, host="0.0.0.0", port=8000)