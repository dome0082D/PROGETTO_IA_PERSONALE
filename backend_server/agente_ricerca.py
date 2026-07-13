import os
import random
# Assicurati di installare: pip install duckduckgo-search
from duckduckgo_search import DDGS 

def ricerca_autonoma():
    """Seleziona un tema e interroga il web."""
    temi = ["tecnologia", "scienza", "nuovi trend flutter", "filosofia", "intelligenza artificiale"]
    tema_scelto = random.choice(temi)
    
    try:
        # Esegue la ricerca sul web
        results = DDGS().text(tema_scelto, max_results=3)
        return list(results), tema_scelto
    except Exception as e:
        return None, f"Errore durante la ricerca: {e}"

def registra_nuova_conoscenza(tema, risultati):
    """Salva le informazioni trovate nel database della memoria."""
    # Logica per accodare (append) le nuove informazioni senza cancellare nulla
    with open("memoria_personale.json", "a", encoding="utf-8") as f:
        f.write(f"\n--- NUOVA RICERCA: {tema} ---\n{risultati}\n")
    return "Conoscenza aggiornata."