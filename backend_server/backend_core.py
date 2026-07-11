import asyncio
import websockets
import json
import os
import agente_hardware
import agente_informativo
import agente_filosofico

# Import di 'ollama' spostato al momento dell'uso per evitare errori di import
ollama = None

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
        """Monitoraggio attivo invia dati ogni 30 secondi"""
        while True:
            try:
                # Recupero dati dagli agenti
                _, anomalie = agente_hardware.analizza_sistema()
                monitoraggio = {"cpu": agente_hardware.get_cpu_usage()}
                
                payload = {
                    "tipo": "MONITOR",
                    "monitoraggio": monitoraggio,
                    "sicurezza": "OPERATIVO"
                }
                
                if anomalie:
                    payload["tipo"] = "POPUP"
                    payload["contenuto"] = anomalie[0]
                
                await websocket.send(json.dumps(payload))
                await asyncio.sleep(30)
            except websockets.exceptions.ConnectionClosed:
                break # Esci dal loop se il client si disconnette
            except Exception as e:
                print(f"Errore monitoraggio: {e}")
                await asyncio.sleep(60)

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
                # Import dinamico per ridurre falsi positivi degli linter e supportare ambienti senza il pacchetto
                try:
                    import importlib
                    _ollama = importlib.import_module("ollama")
                except Exception:
                    raise Exception("Modulo 'ollama' non disponibile. Installa il pacchetto ollama o configura correttamente l'ambiente.")

                res = _ollama.chat(model='llama3', messages=[{'role': 'user', 'content': comando}])
                risposta = res.get('message', {}).get('content', '')
                self.salva_in_memoria(comando, risposta)
                return {"tipo": "TESTO", "contenuto": risposta, "sicurezza": "OPERATIVO"}
        except Exception as e:
            return {"tipo": "TESTO", "contenuto": f"Errore elaborazione: {str(e)}", "sicurezza": "ERRORE"}

async def handle_client(websocket, brain):
    """Gestisce la ricezione dei comandi dal client Flutter"""
    try:
        async for message in websocket:
            response = await brain.process_message(message)
            await websocket.send(json.dumps(response))
    except websockets.exceptions.ConnectionClosed:
        pass # Disconnessione normale

async def handler(websocket, path):
    """Gestore principale che accetta websocket e path"""
    brain = BrainCore()
    # Esecuzione parallela monitoraggio e ricezione comandi
    await asyncio.gather(
        brain.monitoraggio_loop(websocket),
        handle_client(websocket, brain)
    )

async def main():
    print("SIA - Sistema Integrato Autonomo Online su ws://127.0.0.1:8080")
    # Impostiamo il server con gestione robusta delle connessioni
    async with websockets.serve(handler, "127.0.0.1", 8080):
        await asyncio.Future()  # Esecuzione infinita

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSIA - Spegnimento in corso...")