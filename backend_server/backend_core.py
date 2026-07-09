import asyncio
import websockets
import json
try:
    import importlib
    ollama = importlib.import_module("ollama")
except Exception:  # pragma: no cover - provide clear error if missing at runtime
    class _OllamaStub:
        @staticmethod
        def chat(*args, **kwargs):
            raise RuntimeError(
                "Missing 'ollama' package. Install it or ensure it's importable to use AI features."
            )

    ollama = _OllamaStub()
import os
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
        """Monitoraggio attivo invia dati ogni 30 secondi"""
        while True:
            try:
                report, anomalie = agente_hardware.analizza_sistema()
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
            except Exception as e:
                print(f"Errore monitoraggio: {e}")
                await asyncio.sleep(60)

    async def process_message(self, message):
        try:
            data = json.loads(message)
            comando = data.get("comando_testuale", "").lower()
            
            if "meteo" in comando:
                dati = agente_informativo.esegui("meteo")
                return {"tipo": "TABELLA", "contenuto": dati, "sicurezza": "OPERATIVO"}
            
            elif "news" in comando:
                dati = agente_informativo.esegui("news")
                return {"tipo": "LISTA", "contenuto": dati, "sicurezza": "OPERATIVO"}
                
            elif "rifletti" in comando or "mondo" in comando:
                riflessione = agente_filosofico.rifletti_sul_mondo(agente_informativo.esegui("news"))
                return {"tipo": "TESTO", "contenuto": riflessione, "sicurezza": "FILOSOFICO"}
                
            else:
                # Correzione: Gestione errori specifica per Ollama
                try:
                    res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': comando}])
                    risposta = res['message']['content']
                    self.salva_in_memoria(comando, risposta)
                    return {"tipo": "TESTO", "contenuto": risposta, "sicurezza": "OPERATIVO"}
                except Exception as ollama_e:
                    return {"tipo": "TESTO", "contenuto": f"Errore AI: {str(ollama_e)}", "sicurezza": "ERRORE"}
        except Exception as e:
            return {"tipo": "TESTO", "contenuto": f"Errore: {str(e)}", "sicurezza": "ERRORE"}

async def handle_client(websocket, brain):
    """Gestisce la ricezione dei comandi dal client"""
    try:
        async for message in websocket:
            response = await brain.process_message(message)
            await websocket.send(json.dumps(response))
    except Exception as e:
        print(f"Connessione chiusa o errore: {e}")

async def handler(websocket, path):
    """Gestore principale delle connessioni WebSocket con parametro path corretto"""
    brain = BrainCore()
    # Esecuzione parallela monitoraggio e ricezione messaggi
    await asyncio.gather(
        brain.monitoraggio_loop(websocket),
        handle_client(websocket, brain)
    )
except Exception as e:
    print(f"Errore connessione: {e}")
async def main():
    print("SIA - Sistema Integrato Autonomo Online su ws://127.0.0.1:8080")
    async with websockets.serve(handler, "127.0.0.1", 8080):
        await asyncio.Future()  # Esecuzione infinita
if __name__ == "__main__":
    asyncio.run(main())
