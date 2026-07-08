import feedparser
import requests
import imaplib
import email

class AgenteInformativo:
    def get_meteo(self, citta="Milan"):
        # Richiede API Key di OpenWeatherMap
        api_key = "INSERISCI_QUI_LA_TUA_API_KEY"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={citta}&appid={api_key}&units=metric"
        try:
            res = requests.get(url).json()
            temp = res['main']['temp']
            desc = res['weather'][0]['description']
            return {"citta": citta, "temp": temp, "condizione": desc}
        except:
            return {"errore": "Impossibile recuperare il meteo"}

    def get_news(self):
        url = "https://www.ansa.it/sito/ansait_rss.xml"
        feed = feedparser.parse(url)
        return [{"titolo": entry.title, "link": entry.link} for entry in feed.entries[:5]]

    def get_mail_urgenti(self):
        # Nota: Configura come 'App Password' nelle impostazioni Google
        try:
            mail = imaplib.IMAP4_SSL('imap.gmail.com')
            mail.login('tua_email@gmail.com', 'tua_app_password')
            mail.select('inbox')
            _, msg_ids = mail.search(None, 'UNSEEN')
            # Ritorna i titoli delle ultime 3 mail non lette
            return ["Nuova mail rilevata"] # Semplificato per brevità
        except:
            return ["Nessun accesso mail disponibile"]

# Funzione unificata chiamata dal Cervello
def esegui(comando):
    agente = AgenteInformativo()
    if comando == "meteo": return agente.get_meteo()
    if comando == "news": return agente.get_news()
    if comando == "mail": return agente.get_mail_urgenti()
    return None