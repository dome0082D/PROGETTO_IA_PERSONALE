# agente_grafico.py
def crea_rappresentazione(tipo, dati):
    """
    Trasforma dati complessi in strutture JSON che Flutter sa interpretare.
    Esempio: tipo='METEO' -> genera una tabella con icone e temperature.
    """
    if tipo == 'METEO':
        return {"tipo": "TABELLA", "contenuto": dati}
    elif tipo == 'FILOSOFIA':
        return {"tipo": "IMMAGINE_PROMPT", "contenuto": "Una rappresentazione astratta della connessione umana..."}