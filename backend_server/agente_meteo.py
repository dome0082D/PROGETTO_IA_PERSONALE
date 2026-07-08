import requests

def esegui():
    # Sostituisci con la tua chiave API di OpenWeatherMap (gratuita)
    api_key = "LA_TUA_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q=Milan&appid={api_key}&units=metric"
    try:
        response = requests.get(url).json()
        temp = response['main']['temp']
        desc = response['weather'][0]['description']
        if "rain" in desc:
            return f"ATTENZIONE: Sta per piovere a Milano. {temp}°C, {desc}."
        return f"Meteo Milano: {temp}°C, {desc}."
    except:
        return "Errore nel controllo meteo."