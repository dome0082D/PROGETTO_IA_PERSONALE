import asyncio
import websockets
import json
import os
import ollama  # Assicurati di aver installato il pacchetto con 'pip install ollama'
import agente_hardware
import agente_informativo
import agente_filosofico

class BrainCore:
    def __init__(self):
        self.memory_file = "memoria_personale.json"
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f: 
                json.dump([], f)

    def salva_in_memoria(self, input_user, risposta_ai):
        try:
            with open(self.memory_file, "r+") as f:
                memoria = json.load(f)
                memoria.append({"input": input_user, "risposta": risposta_ai})
                f.seek(0)
                json.dump(memoria, f, indent=4)
        except Exception as e:
            print(f"Errore scrittura memoria: {e}")

    async def monitoraggio_loop(self, websocket):
        """Invia dati di monitoraggio finché la connessione è aperta."""
        try:
            while True:
                _, anomalie = agente_hardware.analizza_sistema()
                monitoraggio = {"cpu": agente_hardware.get_cpu_usage()}
                
                payload = {
                    "tipo": "MONITOR",
                    "monitoraggio": monitoraggio,
                    "sicurezza": "OPERATIVO"
                }
                
                if anomalie:
                    payload.update({"tipo": "POPUP", "contenuto": anomalie[0]})
                
                await websocket.send(json.dumps(payload))
                await asyncio.sleep(30)
        except Exception:
            pass # Il ciclo termina pulitamente quando il socket si chiude

    async def process_message(self, message):
        try:
            data = json.loads(message)
            comando = data.get("comando_testuale", "").lower()
            
            if "meteo" in comando:
                return {"tipo": "TABELLA", "contenuto": agente_informativo.esegui("meteo"), "sicurezza": "OPERATIVO"}
            
            elif "news" in comando:
                return {"tipo": "LISTA", "contenuto": agente_informativo.esegui("news"), "sicurezza": "OPERATIVO"}
                
            elif "rifletti" in comando or "mondo" in comando:
                return {"tipo": "TESTO", "contenuto": agente_filosofico.rifletti_sul_mondo(agente_informativo.esegui("news")), "sicurezza": "FILOSOFICO"}
                
            else:
                # Utilizzo standard di Ollama
                res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': comando}])
                risposta = res['message']['content']
                self.salva_in_memoria(comando, risposta)
                return {"tipo": "TESTO", "contenuto": risposta, "sicurezza": "OPERATIVO"}
        except Exception as e:
            return {"tipo": "TESTO", "contenuto": f"Errore AI: {str(e)}", "sicurezza": "ERRORE"}

async def handler(websocket, path):
    """Gestore unico: il monitoraggio e l'ascolto sono legati al ciclo della connessione."""
    brain = BrainCore()
    
    # 1. Creiamo il task di monitoraggio legato a questa specifica connessione
    monitor_task = asyncio.create_task(brain.monitoraggio_loop(websocket))
    
    try:
        # 2. Ascolto attivo dei messaggi
        async for message in websocket:
            response = await brain.process_message(message)
            await websocket.send(json.dumps(response))
    finally:
        # 3. Se la connessione cade, chiudiamo il monitoraggio
        monitor_task.cancel()

async def main():
    print("SIA - Sistema Integrato Autonomo Online su ws://127.0.0.1:8080")
    async with websockets.serve(handler, "127.0.0.1", 8080):
        await asyncio.Future()  # Esecuzione infinita

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSIA - Spegnimento in corso...")