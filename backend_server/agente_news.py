import feedparser

def esegui():
    url = "https://www.ansa.it/sito/ansait_rss.xml"
    feed = feedparser.parse(url)
    notizie = [entry.title for entry in feed.entries[:3]]
    return "Notizie dal mondo: " + " | ".join(notizie)