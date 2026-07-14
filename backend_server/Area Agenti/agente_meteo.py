import requests
import os

def controlla_meteo(citta="Milano"):
    """
    Funzione principale che fa la chiamata a OpenWeatherMap.
    """
    # Cerca la chiave API nelle variabili di sistema, altrimenti usa il placeholder
    api_key = os.getenv("OPENWEATHER_API_KEY", "LA_TUA_API_KEY")
    if api_key == "LA_TUA_API_KEY":
        return "Errore: Inserisci la tua API Key di OpenWeatherMap nel codice o nelle variabili d'ambiente."
        
    # Aggiunto &lang=it per avere la descrizione in italiano
    url = f"http://api.openweathermap.org/data/2.5/weather?q={citta}&appid={api_key}&units=metric&lang=it"
    
    try:
        response = requests.get(url).json()
        
        # Controllo se la città esiste ed è valida
        if response.get("cod") != 200:
            return f"Errore nel controllo meteo per {citta}: {response.get('message', 'Città non trovata')}."
            
        temp = response['main']['temp']
        desc = response['weather'][0]['description'].lower()
        
        # Manteniamo la tua logica di avviso, estesa per l'italiano
        if "pioggia" in desc or "rain" in desc or "rovesci" in desc:
            return f"ATTENZIONE: Sta per piovere a {citta.capitalize()}. {temp}°C, {desc.capitalize()}."
            
        return f"Meteo {citta.capitalize()}: {temp}°C, {desc.capitalize()}."
        
    except Exception as e:
        return f"Errore nel controllo meteo: {e}"

# --- INTERFACCIA PER IL NUOVO LOADER MODULARE ---
def esegui(comando=""):
    """
    Funzione standard di interfaccia per l'architettura modulare di SIA.
    Cerca di capire se hai chiesto una città specifica.
    """
    cmd = comando.lower() if comando else ""
    citta = "Milano" # La tua città di default
    
    # Tentativo di estrarre la città dal comando (es: "meteo a Roma")
    parole = cmd.split()
    for preposizione in ["a", "per", "di"]:
        if preposizione in parole:
            idx = parole.index(preposizione)
            if idx + 1 < len(parole):
                citta = parole[idx + 1].replace("?", "").strip().capitalize()
                break
                
    return controlla_meteo(citta)