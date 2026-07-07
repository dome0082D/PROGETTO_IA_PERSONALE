import cv2

def scansiona():
    """Modulo di visione reale che interroga la webcam del sistema."""
    try:
        # Tentiamo di aprire la camera
        cap = cv2.VideoCapture(0)
        # Verifichiamo se il segnale è valido
        success, frame = cap.read()
        cap.release()
        
        if success:
            return "Visione Spaziale: ATTIVA"
        else:
            return "Visione Spaziale: CAMERA_NON_DISPONIBILE"
    except Exception as e:
        return f"Visione Spaziale: ERRORE_{str(e)}"