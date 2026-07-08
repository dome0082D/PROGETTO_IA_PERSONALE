import asyncio
import websockets
import json
import ollama
import os

class BrainCore:
    def __init__(self):
        self.memory_file = "memoria_personale.json"
        if not os.path.exists(self.memory_file):
            with open(self.memory_file, "w") as f: 
                json.dump([], f)

    def salva_in_memoria(self, input_user, risposta_ai):
        with open(self.memory_file, "r+") as f:
            memoria = json.load(f)
            memoria.append({"input": input_user, "risposta": risposta_ai})
            f.seek(0)
            json.dump(memoria, f, indent=4)

    def leggi_memoria_recente(self):
        with open(self.memory_file, "r") as f:
            try:
                memoria = json.load(f)
                return str(memoria[-5:])
            except:
                return ""

    async def handle_file(self, file_path):
        try:
            res = ollama.chat(model='llava', messages=[{
                'role': 'user',
                'content': 'Analizza questo file o immagine e spiegami cosa contiene e cosa dovrei fare.',
                'images': [file_path]
            }])
            risposta = res['message']['content']
            self.salva_in_memoria(f"File: {file_path}", risposta)
            return {"domanda": risposta, "sicurezza": "ANALISI COMPLETATA"}
        except Exception as e:
            return {"feedback": f"Errore: {str(e)}"}

    async def handle_text(self, text):
        contesto = self.leggi_memoria_recente()
        prompt = f"Contesto precedente: {contesto}. Domanda attuale: {text}"
        res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
        risposta = res['message']['content']
        self.salva_in_memoria(text, risposta)
        return {"domanda": risposta, "sicurezza": "PENSIERO ATTIVO"}

    async def process_message(self, message):
        data = json.loads(message)
        if "file_caricato" in data:
            return await self.handle_file(data["file_caricato"])
        elif "comando_testuale" in data:
            return await self.handle_text(data["comando_testuale"])
        return {"feedback": "Comando non riconosciuto."}

async def handler(websocket, path):
    brain = BrainCore()
    async for message in websocket:
        response = await brain.process_message(message)
        await websocket.send(json.dumps(response))

if __name__ == "__main__":
    start_server = websockets.serve(handler, "127.0.0.1", 8080)
    print("Cervello Centrale avviato su ws://127.0.0.1:8080")
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()