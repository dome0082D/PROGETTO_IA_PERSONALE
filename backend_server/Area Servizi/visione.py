# VISIONE.PY - Modulo reale
import cv2

def scansiona():
    """Accede alla webcam reale del sistema"""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            return "Visione Spaziale: ATTIVA"
        else:
            return "Visione Spaziale: ERRORE_CAMERA"
    except Exception as e:
        return f"Visione Spaziale: ERRORE {str(e)}"