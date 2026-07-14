import json

def crea_rappresentazione(tipo, dati):
    """
    Trasforma dati complessi in strutture JSON che l'app Flutter sa interpretare.
    Ritorna un dizionario pronto per essere serializzato in JSON via WebSocket.
    """
    tipo_up = tipo.upper()
    
    if tipo_up == 'METEO':
        # Esempio: genera una griglia/tabella con temperature, icone e umidità
        return {
            "componente": "METEO_CARD",
            "dati": {
                "temperatura": dati.get("temperatura", "N/D"),
                "condizione": dati.get("condizione", "Generico"),
                "icona": dati.get("icona", "weather_sunny"),
                "dettagli": {
                    "umidita": dati.get("umidita", "N/D"),
                    "vento": dati.get("vento", "N/D"),
                    "localita": dati.get("localita", "Milano")
                }
            }
        }
        
    elif tipo_up == 'FILOSOFIA':
        # Ritorna un prompt grafico strutturato per l'interfaccia
        return {
            "componente": "FILOSOFIA_VIEW",
            "dati": {
                "testo_riflessione": dati.get("testo", ""),
                "prompt_immagine": f"Digital art, highly detailed, deep philosophical concept: {dati.get('prompt_suggerito', 'Una mente digitale che riflette nel vuoto dello spazio')}",
                "stile": "cyberpunk_surrealism"
            }
        }

    elif tipo_up == 'HARDWARE':
        # Per monitorare l'i3 o altri componenti hardware con un grafico a ciambella/barra
        return {
            "componente": "HARDWARE_MONITOR",
            "dati": {
                "cpu_usage": dati.get("cpu", 0),
                "ram_usage": dati.get("ram", 0),
                "temperatura_cpu": dati.get("temp", 0),
                "labels": ["Uso", "Libero"]
            }
        }

    elif tipo_up == 'LISTA_PRODOTTI':
        # Ottimo per scambi ("Re-love") o tracciamento prezzi ("Retail-Scout")
        return {
            "componente": "PRODOTTI_LIST",
            "dati": {
                "elementi": dati.get("prodotti", []),  # Lista di dizionari {nome, prezzo/valore, icona/immagine}
                "totale_elementi": len(dati.get("prodotti", []))
            }
        }

    # Fallback generico se il tipo non è riconosciuto
    return {
        "componente": "TESTO_SEMPLICE",
        "dati": {
            "testo": str(dati)
        }
    }


def esegui(comando, dati=None):
    """
    Interfaccia standard per il caricamento dinamico.
    Si aspetta che 'dati' sia un dizionario. Se è una stringa JSON, fa il parsing automatico.
    """
    if dati is None:
        dati = {}
        
    if isinstance(dati, str):
        try:
            dati = json.loads(dati)
        except Exception:
            dati = {"testo": dati}
            
    # Determina il tipo di rappresentazione analizzando il comando o i dati stessi
    tipo = dati.get("tipo_richiesto", "TESTO_SEMPLICE")
    if "meteo" in comando.lower():
        tipo = "METEO"
    elif "filosofia" in comando.lower() or "rifletti" in comando.lower():
        tipo = "FILOSOFIA"
    elif "hardware" in comando.lower() or "risorse" in comando.lower():
        tipo = "HARDWARE"
        
    return crea_rappresentazione(tipo, dati)