import uuid
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal

class MessaggioClient(BaseModel):
    """
    Formato ufficiale dei messaggi in ingresso.
    Dal semplice testo, fino all'invio di file complessi per l'assimilazione visiva.
    """
    # Identificazione e tracciamento per i log 24/7
    id_messaggio: str = Field(default_factory=lambda: str(uuid.uuid4()), description="ID univoco per tracciare l'evento o l'errore")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Marca temporale esatta per l'apprendimento cronologico")
    
    # Origine e tipo
    mittente: Literal["windows", "android", "admin", "sistema_sicurezza"]
    tipo: Literal["testo", "immagine", "video", "documento", "avviso_sicurezza", "heartbeat"]
    
    # Contenuto effettivo
    contenuto: str = Field(description="Testo dell'utente o descrizione sintetica dell'evento")
    
    # --- PREDISPOSIZIONE LUNGIMIRANTE (Assimilazione File) ---
    file_base64: Optional[str] = Field(default=None, description="Stringa del file codificato (es. la foto del foglio turni da analizzare)")
    estensione_file: Optional[str] = Field(default=None, description="Formato del file. Es. 'jpg', 'png', 'mp4', 'pdf'")
    
    # Dati di contesto variabili
    dati_extra: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadati (es. livello batteria Android, telemetria)")


class AzioneIA(BaseModel):
    """
    Formato ufficiale dei comandi in uscita.
    Ciò che l'IA ordina di fare al mondo reale o ai dispositivi connessi.
    """
    id_azione: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp_creazione: str = Field(default_factory=lambda: datetime.now().isoformat())
    
    # Destinazione e urgenza
    target: Literal["windows", "android", "broadcast", "core"]
    priorita: Literal["bassa", "normale", "alta", "critica"] = Field(default="normale", description="Urgenza dell'azione (es. 'critica' per sicurezza)")
    
    # Azione e parametri operativi
    azione: str = Field(description="Comando. Es: 'SET_ALARM', 'GENERATE_IMAGE', 'SPEAK_AND_ANIMATE', 'UPDATE_MEMORY'")
    parametri: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Dettagli operativi. Es: {'orario_sveglia': '06:30', 'prompt_immagine': '...', 'giorni': ['lunedì', 'martedì']}"
    )
    
    # Output vocale/visivo opzionale
    testo_parlato: Optional[str] = Field(default=None, description="Frase che il sintetizzatore vocale del dispositivo dovrà pronunciare")