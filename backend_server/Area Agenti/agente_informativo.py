import feedparser
import requests
import imaplib
import email
import os

class AgenteInformativo:
    def get_meteo(self, citta="Milan"):
        # Cerca l'API Key nelle variabili d'ambiente, altrimenti usa il segnaposto
        api_key = os.getenv("OPENWEATHER_API_KEY", "INSERISCI_QUI_LA_TUA_API_KEY")
        if api_key == "INSERISCI_QUI_LA_TUA_API_KEY":
            return {"errore": "Configura la tua API Key di OpenWeatherMap per vedere il meteo."}
            
        url = f"http://api.openweathermap.org/data/2.5/weather?q={citta}&appid={api_key}&units=metric&lang=it"
        try:
            res = requests.get(url).json()
            if res.get("cod") != 200:
                return {"errore": f"Città non trovata o errore API: {res.get('message', '')}"}
            temp = res['main']['temp']
            desc = res['weather'][0]['description']
            return {"citta": citta, "temp": f"{temp}°C", "condizione": desc.capitalize()}
        except Exception as e:
            return {"errore": f"Impossibile recuperare il meteo: {e}"}

    def get_news(self):
        try:
            url = "https://www.ansa.it/sito/ansait_rss.xml"
            feed = feedparser.parse(url)
            if not feed.entries:
                return [{"titolo": "Nessuna notizia disponibile al momento.", "link": ""}]
            return [{"titolo": entry.title, "link": entry.link} for entry in feed.entries[:5]]
        except Exception as e:
            return [{"titolo": f"Errore nel caricamento delle notizie ANSA: {e}", "link": ""}]

    def get_mail_urgenti(self):
        # Cerca le credenziali Gmail nelle variabili d'ambiente, altrimenti usa i segnaposto
        email_user = os.getenv("SIA_EMAIL", "tua_email@gmail.com")
        email_pass = os.getenv("SIA_EMAIL_PASSWORD", "tua_app_password")
        
        if email_user == "tua_email@gmail.com" or email_pass == "tua_app_password":
            return ["Configura le tue credenziali Gmail nelle variabili d'ambiente per leggere le mail."]
            
        try:
            # Connessione sicura IMAP a Gmail
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login(email_user, email_pass)
            mail.select('inbox')
            
            # Cerca solo i messaggi NON letti
            status, response = mail.search(None, 'UNSEEN')
            if status != 'OK':
                return ["Errore durante la ricerca delle email non lette."]
                
            msg_ids = response[0].split()
            if not msg_ids:
                return ["Nessuna nuova email non letta in arrivo."]
                
            risultati = []
            # Prende le ultime 3 email non lette (le più recenti sono alla fine della lista)
            for msg_id in reversed(msg_ids[-3:]):
                status, data = mail.fetch(msg_id, '(RFC822)')
                if status != 'OK':
                    continue
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                # Estrae e decodifica l'oggetto e il mittente
                soggetto = msg['Subject'] or "Senza Oggetto"
                mittente = msg['From'] or "Sconosciuto"
                risultati.append(f"Da: {mittente} | Oggetto: {soggetto}")
                
            mail.logout()
            return risultati
        except Exception as e:
            return [f"Errore di accesso alla casella email: {e}"]


# --- INTERFACCIA PER IL NUOVO LOADER MODULARE ---
def esegui(comando):
    """
    Funzione standard che mappa i comandi di testo verso le funzioni dell'agente.
    """
    agente = AgenteInformativo()
    cmd = comando.lower()
    
    # 1. GESTIONE METEO (con tentativo di estrarre la città)
    if "meteo" in cmd or "tempo" in cmd:
        citta = "Milan"
        parole = cmd.split()
        # Se l'utente dice ad esempio "meteo a Roma" o "meteo per Torino"
        for preposizione in ["a", "per"]:
            if preposizione in parole:
                idx = parole.index(preposizione)
                if idx + 1 < len(parole):
                    citta = parole[idx + 1].replace("?", "").strip().capitalize()
                    break
        
        risultato = agente.get_meteo(citta)
        if "errore" in risultato:
            return risultato["errore"]
        return f"Meteo a {risultato['citta']}: {risultato['temp']}, {risultato['condizione']}."
        
    # 2. GESTIONE NEWS
    if "news" in cmd or "notizie" in cmd or "ansa" in cmd:
        notizie = agente.get_news()
        output = "Ecco le ultime 5 notizie da ANSA:\n"
        for i, n in enumerate(notizie, 1):
            output += f"\n{i}. {n['titolo']}\n   Link: {n['link']}"
        return output
        
    # 3. GESTIONE EMAIL
    if "mail" in cmd or "email" in cmd or "posta" in cmd:
        mail = agente.get_mail_urgenti()
        output = "Verifica casella email:\n"
        for m in mail:
            output += f"- {m}\n"
        return output.strip()
        
    return "Comando non riconosciuto dall'Agente Informativo."