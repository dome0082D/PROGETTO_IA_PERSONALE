import feedparser

def recupera_notizie():
    """
    Recupera le prime 3 notizie dal feed RSS dell'ANSA.
    """
    url = "https://www.ansa.it/sito/ansait_rss.xml"
    try:
        feed = feedparser.parse(url)
        # Controllo di sicurezza se il feed è vuoto o non raggiungibile
        if not feed.entries:
            return "Nessuna notizia disponibile al momento dal feed ANSA."
            
        notizie = [entry.title for entry in feed.entries[:3]]
        return "Notizie dal mondo: " + " | ".join(notizie)
    except Exception as e:
        return f"Errore nel recupero delle notizie: {e}"


# --- INTERFACCIA PER IL NUOVO LOADER MODULARE ---
def esegui(comando=""):
    """
    Funzione standard di interfaccia per l'architettura modulare di SIA.
    Accetta il parametro 'comando' (anche se vuoto) per integrarsi con il loader.
    """
    return recupera_notizie()