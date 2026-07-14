# Area_Agenti/agente_visione.py
import os
import base64
import re
from io import BytesIO
from Area_Core.backend_core import CONFIG, logger

# Gestione robusta delle librerie di visione
try:
    from PIL import Image
    import pytesseract
    
    # Fondamentale per i sistemi Windows: specifica il percorso dell'eseguibile Tesseract.
    # Assicurati di aver installato Tesseract-OCR sul tuo PC.
    if os.name == 'nt':
        pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        
except ImportError:
    logger.error("Librerie mancanti per agente_visione. Esegui: pip install Pillow pytesseract")

class AgenteVisione:
    def __init__(self):
        # I file in arrivo vengono salvati nell'area di input
        self.input_dir = CONFIG["PERCORSO_INPUT_FILE"]
        
    def _decodifica_immagine(self, base64_string, nome_file="ultimo_turno_ricevuto.png"):
        """Decodifica il Base64 e salva temporaneamente l'immagine nell'Area Media."""
        try:
            # Rimuove l'eventuale intestazione 'data:image/png;base64,' se inviata dal frontend
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]
                
            # validate=True previene crash se la stringa è corrotta
            image_data = base64.b64decode(base64_string, validate=True)
            image = Image.open(BytesIO(image_data))
            
            percorso_salvataggio = os.path.join(self.input_dir, nome_file)
            image.save(percorso_salvataggio)
            logger.info(f"Immagine salvata per analisi in: {percorso_salvataggio}")
            return image
        except Exception as e:
            logger.error(f"Errore nella decodifica dell'immagine: {e}")
            return None

    def _estrai_orari(self, testo):
        """Cerca orari nel testo (es. 08:30, 14.00, 9:00) per programmare azioni."""
        pattern_orari = r'\b([0-1]?[0-9]|2[0-3])[:.]([0-5][0-9])\b'
        orari_trovati = re.findall(pattern_orari, testo)
        # Formatta i risultati rigorosamente in "HH:MM"
        return [f"{h.zfill(2)}:{m}" for h, m in orari_trovati]

    def analizza_file_base64(self, base64_string):
        """Metodo principale: legge l'immagine, apprende il testo e deduce azioni da eseguire."""
        logger.info("Avviata analisi visiva del file ricevuto.")
        
        immagine = self._decodifica_immagine(base64_string)
        if not immagine:
            return {"tipo": "ERRORE", "contenuto": "Impossibile decodificare l'immagine fornita."}

        try:
            # Estrazione del testo tramite OCR
            testo_estratto = pytesseract.image_to_string(immagine, lang='ita+eng')
            testo_pulito = testo_estratto.strip()
            
            if not testo_pulito:
                return {"tipo": "TESTO", "contenuto": "Ho analizzato il file visivamente, ma non ho rilevato testo leggibile."}
            
            logger.debug(f"Testo estratto: {testo_pulito[:100]}...")

            # --- LOGICA DI ASSIMILAZIONE E AZIONE ---
            orari = self._estrai_orari(testo_pulito)
            
            if orari:
                # Se trova orari (es. uno schedule settimanale), prepara il comando per lo smartphone
                orario_sveglia = orari[0]
                messaggio_azione = (
                    f"Ho letto il documento. Sembra contenere degli orari. "
                    f"Ho preparato un'azione per impostare la sveglia alle {orario_sveglia} sul tuo smartphone."
                )
                
                # Il payload "AZIONE_DISPOSITIVO" comunica a Flutter di attivare l'allarme
                return {
                    "tipo": "AZIONE_DISPOSITIVO",
                    "comando": "IMPOSTA_SVEGLIA",
                    "parametro": orario_sveglia,
                    "contenuto": messaggio_azione,
                    "sicurezza": "PROATTIVO",
                    "memoria_appresa": testo_pulito
                }
            else:
                return {
                    "tipo": "TESTO", 
                    "contenuto": f"Ho assimilato il contenuto del file. Ecco un'anteprima di cosa ho letto:\n{testo_pulito[:200]}...",
                    "memoria_appresa": testo_pulito
                }

        except pytesseract.TesseractNotFoundError:
            logger.error("Eseguibile Tesseract non trovato nel sistema.")
            return {"tipo": "ERRORE", "contenuto": "Motore OCR Tesseract non trovato. Assicurati che sia installato sul sistema."}
        except Exception as e:
            logger.error(f"Errore generale durante l'OCR: {e}")
            return {"tipo": "ERRORE", "contenuto": "Si è verificato un errore imprevisto durante l'analisi visiva."}

# Istanza singola pronta per l'importazione
agente_visivo = AgenteVisione()