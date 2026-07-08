import pytesseract
from PIL import Image

# Nota: Assicurati di avere Tesseract installato sul tuo sistema
# (es. su Windows scarica l'installer di Tesseract OCR)

def analizza_file(percorso_immagine):
    """Legge il testo da un'immagine e lo trasforma in istruzioni."""
    try:
        # Carica l'immagine
        img = Image.open(percorso_immagine)
        # Estrai il testo
        testo_estratto = pytesseract.image_to_string(img)
        
        # Analisi semplice: cerchiamo parole chiave come 'ore', 'turno', 'sveglia'
        if "turno" in testo_estratto.lower() or "ore" in testo_estratto.lower():
            return f"Ho rilevato un programma di lavoro. Dettagli: {testo_estratto[:100]}..."
        
        return f"Ho letto: {testo_estratto[:100]}"
    except Exception as e:
        return f"Errore durante l'analisi: {e}"