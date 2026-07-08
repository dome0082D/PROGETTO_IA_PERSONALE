import asyncio
import websockets
import json
import ollama
import os

class BrainCore:
    def __init__(self):
        self.memory_file = "memoria_personale.json"
        self.command_file = "pending_commands.json"
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f: json.dump([], f)

    def salva_in_memoria(self, input_user, risposta_ai):
        with open(self.memory_file, "r+") as f:
            memoria = json.load(f)
            memoria.append({"input": input_user, "risposta": risposta_ai})
            f.seek(0)
            json.dump(memoria, f, indent=4)

    async def handle_file(self, file_path):
        # LLaVA analizza e il Cervello decide l'azione
        res = ollama.chat(model='llava', messages=[{
            'role': 'user',
            'content': 'Analizza il file. Se c\'è un orario o un impegno, estrai azione e ora in JSON.',
            'images': [file_path]
        }])
        risposta = res['message']['content']
        
        # Esempio di logica: Se il modello rileva un impegno, crea il comando
        comando = {"azione": "IMPOSTA_SVEGLIA", "dettagli": {"ora": "08:00", "descrizione": "Turno"}}
        with open(self.command_file, "w") as f:
            json.dump(comando, f)
            
        return {"domanda": f"Ho analizzato: {risposta}. Ho creato un comando per l'esecutore.", "sicurezza": "OPERATIVO"}

    async def handle_text(self, text):
        res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': text}])
        risposta = res['message']['content']
        self.salva_in_memoria(text, risposta)
        return {"domanda": risposta, "sicurezza": "PENSIERO ATTIVO"}

    async def process_message(self, message):
        data = json.loads(message)
        if "file_caricato" in data:
            return await self.handle_file(data["file_caricato"])
        return await self.handle_text(data.get("comando_testuale", ""))

async def handler(websocket, path):
    brain = BrainCore()
    async for message in websocket:
        response = await brain.process_message(message)
        await websocket.send(json.dumps(response))

if __name__ == "__main__":
    start_server = websockets.serve(handler, "127.0.0.1", 8080)
    print("Cervello Centrale attivo...")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()