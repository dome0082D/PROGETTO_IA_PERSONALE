def analizza_umore(testo):
    if "stress" in testo.lower():
        return "Modalità supportiva attivata"
    return "Modalità colloquiale"