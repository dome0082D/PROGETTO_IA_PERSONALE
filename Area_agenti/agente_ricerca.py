import os
import random
import json
import datetime
# Importazione corretta dell'ultima versione della libreria (pip install duckduckgo-search)
from duckduckgo_search import DDGS

# Percorso della memoria condiviso
FILE_MEMORIA = "memoria_personale.json"

def esegui_ricerca_web(query):
    """
    Motore centrale per interrogare il web in modo sicuro.
    Ritorna una lista di risultati puliti.
    """
    try:
        risultati_trovati = []
        with DDGS() as ddgs:
            # max_results impostato a 3 per essere veloci, puoi aumentarlo se serve
            risultati = list(ddgs.text(query, max_results=3))
            
            for res in risultati:
                risultati_trovati.append({
                    "titolo": res.get("title", ""),
                    "testo": res.get("body", ""),
                    "link": res.get("href", "")
                })
        return risultati_trovati
    except Exception as e:
        return f"Errore durante la navigazione web (possibile blocco provider o assenza rete): {e}"

def ricerca_autonoma():
    """
    Sceglie un tema rilevante dai tuoi interessi e interroga il web per espandere la conoscenza 24/7.
    """
    temi = [
        "tecnologia hardware i3 ottimizzazione", 
        "scienza e scoperte recenti spaziali", 
        "nuovi trend sviluppo Flutter", 
        "filosofia e testi apocrifi libro di enoch", 
        "intelligenza artificiale generativa open source",
        "novità framework Node.js backend",
        "ottimizzazione prestazioni Vercel deploy"
    ]
    tema_scelto = random.choice(temi)
    risultati = esegui_ricerca_web(tema_scelto)
    
    return risultati, tema_scelto

def registra_nuova_conoscenza(tema, risultati, tipo_ricerca="autonoma"):
    """
    Salva le informazioni trovate in modo strutturato nel database JSON.
    Garantisce che il file JSON non si corrompa.
    """
    if non risultati o isinstance(risultati, str):
        return "Nessuna conoscenza valida trovata da registrare."
        
    dati_memoria = {"ricerche_salvate": []}
    
    # 1. Carica il file esistente (se c'è) per non sovrascrivere i vecchi dati
    if os.path.exists(FILE_MEMORIA):
        try:
            with open(FILE_MEMORIA, "r", encoding="utf-8") as f:
                contenuto_esistente = json.load(f)
                if isinstance(contenuto_esistente, dict):
                    dati_memoria = contenuto_esistente
                    if "ricerche_salvate" not in dati_memoria:
                        dati_memoria["ricerche_salvate"] = []
        except json.JSONDecodeError:
            pass # Se il file è rotto, lo ricrea pulito

    # 2. Prepara il blocco della nuova scoperta
    nuova_scoperta = {
        "timestamp": str(datetime.datetime.now()),
        "tipo_ricerca": tipo_ricerca,
        "tema_o_query": tema,
        "dati": risultati
    }
    
    # 3. Accoda la nuova informazione
    dati_memoria["ricerche_salvate"].append(nuova_scoperta)
    
    # 4. Salva scrivendo un JSON formattato perfettamente
    try:
        with open(FILE_MEMORIA, "w", encoding="utf-8") as f:
            json.dump(dati_memoria, f, indent=4, ensure_ascii=False)
        return f"Conoscenza su '{tema}' assimilata nel database."
    except Exception as e:
        return f"Errore salvataggio memoria: {e}"


# --- INTERFACCIA PER IL NUOVO LOADER MODULARE ---
def esegui(comando=""):
    """
    Interfaccia standard. Gestisce sia le ricerche mirate che lo studio autonomo.
    """
    cmd = comando.lower().strip()
    
    # 1. RICERCA AUTONOMA (SIA studia da sola)
    if cmd == "" or any(parola in cmd for parola in ["esplora", "studia", "impara", "aggiornati"]):
        risultati, tema = ricerca_autonoma()
        
        if isinstance(risultati, str): # Significa che ha restituito un errore
            return f"SIA Ricerca: {risultati}"
            
        esito = registra_nuova_conoscenza(tema, risultati, tipo_ricerca="autonoma")
        
        risposta = f"SIA Studio Autonomo completato.\nHo approfondito: '{tema}'.\n"
        for res in risultati:
            risposta += f"- {res['titolo']}\n"
        risposta += f"\n{esito}"
        return risposta

    # 2. RICERCA MIRATA (Tu le chiedi di cercare qualcosa)
    elif any(parola in cmd for parola in ["cerca", "trova", "cercami", "googla", "internet"]):
        # Estrapoliamo la query rimuovendo i comandi base
        query = cmd
        da_rimuovere = ["cerca su internet", "cerca", "trova", "cercami", "googla", "su internet", "nel web", "sia"]
        for p in da_rimuovere:
            query = query.replace(p, "").strip()
            
        if not query:
            return "Cosa vuoi che cerchi? Prova a dirmi: 'SIA, cerca novità su Flutter'."
            
        risultati = esegui_ricerca_web(query)
        
        if isinstance(risultati, str): # Gestione errori
            return f"SIA Ricerca: {risultati}"
            
        esito = registra_nuova_conoscenza(query, risultati, tipo_ricerca="mirata")
        
        risposta = f"SIA Risultati Ricerca per: '{query}'\n\n"
        for res in risultati:
            risposta += f"🔹 {res['titolo']}\n   {res['link']}\n   {res['testo'][:150]}...\n\n"
        risposta += f"*{esito}*"
        return risposta
        
    return "L'Agente Ricerca è pronto. Dì 'cerca [argomento]' oppure 'esplora' per l'apprendimento autonomo."