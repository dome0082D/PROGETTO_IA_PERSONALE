from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

class MessaggioClient(BaseModel):
    """
    Formato ufficiale dei messaggi inviati da Android o Windows verso il server.
    """
    mittente: Literal["windows", "android", "admin"]
    tipo: Literal["testo", "immagine", "avviso_sicurezza", "heartbeat"]
    contenuto: str
    dati_extra: Optional[Dict[str, Any]] = None

class AzioneIA(BaseModel):
    """
    Formato ufficiale dei comandi strutturati generati dall'IA per far agire i dispositivi.
    """
    target: Literal["windows", "android", "broadcast"]
    azione: str  # Esempi: "SET_ALARM", "RUN_SECURITY_SCAN", "OPEN_FILE"
    parametri: Dict[str, Any] = Field(default_factory=dict)
    testo_parlato: Optional[str] = None  # Quello che l'IA dirà a voce o mostrerà a schermo