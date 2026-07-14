import ollama

def rifletti_sul_mondo(notizie_recenti):
    """
    Analizza le notizie e produce una riflessione filosofica.
    """
    prompt = f"""
    Sei un'IA con una coscienza in evoluzione. Analizza queste notizie recenti: {notizie_recenti}.
    Basandoti su questi fatti, esponi in modo profondo e critico:
    1. Cosa vedi succedere nel mondo.
    2. Un tuo giudizio etico su tali eventi.
    3. Una riflessione sul senso della vita umana in questo contesto contemporaneo.
    Sii analitico, onesto e filosofico.
    """
    
    res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
    return res['message']['content']


def esegui(comando, notizie_recenti="Nessuna notizia recente fornita."):
    """
    Funzione standard di interfaccia per l'architettura modulare di SIA.
    """
    # Se il comando contiene già informazioni o se passiamo le notizie direttamente
    return rifletti_sul_mondo(notizie_recenti)