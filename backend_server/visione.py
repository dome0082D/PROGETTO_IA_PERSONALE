import cv2
import logging

logger = logging.getLogger("VisioneSpaziale")

def avvio_occhi():
    # Inizializza la webcam principale
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        logger.error("Visione non disponibile: Webcam non trovata.")
        return None
    logger.info("Sistema Visione Spaziale attivo.")
    return cap

def analizza_frame(cap):
    ret, frame = cap.read()
    if ret:
        # Qui potremmo inserire il riconoscimento volti in futuro
        return "PRESENZA_RILEVATA"
    return "VUOTO"