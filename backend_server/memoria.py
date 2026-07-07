import json
import os

def salva_evento(tipo, dettagli):
    file_path = "apprendimento.json"
    if not os.path.exists(file_path):
        with open(file_path, "w") as f: json.dump([], f)
    
    with open(file_path, "r+") as f:
        data = json.load(f)
        data.append({"tipo": tipo, "dettagli": dettagli})
        f.seek(0)
        json.dump(data, f, indent=4)