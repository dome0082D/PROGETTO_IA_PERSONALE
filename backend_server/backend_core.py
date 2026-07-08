import asyncio
import websockets
import json
import ollama
import os
import agente_hardware
import agente_informativo
import agente_filosofico
import agente_grafico

class BrainCore:
    def __init__(self):
        self.memory_file = "memoria_personale.json"
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f: json.dump([], f)

    def salva_in_memoria(self, input_user, risposta_ai):
        with open(self.memory_file, "r+") as f:
            try:
                memoria = json.load(f)
            except:
                memoria = []
            memoria.append({"input": input_user, "risposta": risposta_ai})
            f.seek(0)
            json.dump(memoria, f, indent=4)

    async def monitoraggio_loop(self, websocket):
        """Monitoraggio attivo in background"""
        while True:
            try:
                report, anomalie = agente_hardware.analizza_sistema()
                monitoraggio = {"cpu": agente_hardware.get_cpu_usage()} # Assicurati di avere questa funzione
                
                if anomalie:
                    # Invia avviso proattivo
                    await websocket.send(json.dumps({"tipo": "POPUP", "msg": anomalie[0], "monitoraggio": monitoraggio}))
                
                await asyncio.sleep(30) # Check ogni 30 secondi
            except Exception as e:
                print(f"Errore monitoraggio: {e}")
                await asyncio.sleep(60)

    async def process_message(self, message):
        data = json.loads(message)
        comando = data.get("comando_testuale", "").lower()
        
        # Dispatcher
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
            res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': comando}])
            risposta = res['message']['content']
            self.salva_in_memoria(comando, risposta)
            return {"tipo": "TESTO", "contenuto": risposta, "sicurezza": "OPERATIVO"}

async def handler(websocket, path):
    brain = BrainCore()
    # Esegue in parallelo il monitoraggio e la ricezione messaggi
    await asyncio.gather(
        brain.monitoraggio_loop(websocket),
        brain.handle_messages(websocket, brain)
    )

async def handle_messages(websocket, brain):
    async for message in websocket:
        response = await brain.process_message(message)
        await websocket.send(json.dumps(response))

if __name__ == "__main__":
    print("SIA - Sistema Integrato Autonomo Online...")
    start_server = websockets.serve(handler, "127.0.0.1", 8080)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()