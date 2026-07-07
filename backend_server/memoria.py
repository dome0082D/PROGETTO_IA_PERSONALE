import json
import os

class MemoriaApprendimento:
    def __init__(self, file_path="apprendimento.json"):
        self.file_path = file_path
        if not os.path.exists(self.file_path):
            with open(self.file_path, "w") as f:
                json.dump([], f)

    def salva_evento(self, tipo, dettagli):
        with open(self.file_path, "r+") as f:
            dati = json.load(f)
            dati.append({"tipo": tipo, "dettagli": dettagli})
            f.seek(0)
            json.dump(dati, f, indent=4)