"""
Modulo: agente_social_mail.py
Descrizione: Centrale di controllo avanzata per la gestione unificata di Email e Social.
"""

import imaplib
import email
from email.header import decode_header
import os
import re

def decodifica_testo(testo):
    """Decodifica i titoli delle mail gestendo UTF-8 e caratteri speciali."""
    try:
        if not testo: return "Senza Oggetto"
        decoded_header = decode_header(testo)
        decoded_text = ""
        for part, encoding in decoded_header:
            if isinstance(part, bytes):
                decoded_text += part.decode(encoding or 'utf-8', errors='replace')
            else:
                decoded_text += part
        return decoded_text
    except Exception:
        return str(testo)

def pulisci_mittente(mittente):
    """Estrae solo il nome o l'email pulita da stringhe tipo 'Nome Cognome <email@example.com>'."""
    match = re.search(r'<(.*?)>', mittente)
    return match.group(1) if match else mittente

def leggi_mail():
    """Connessione sicura, lettura e chiusura garantita della sessione."""
    user = os.getenv("SIA_EMAIL", "tua_email@gmail.com")
    pw = os.getenv("SIA_EMAIL_PASSWORD", "tua_app_password")
    
    if user == "tua_email@gmail.com":
        return ["Configura le credenziali (SIA_EMAIL/PASSWORD) nelle variabili di sistema."]

    mail = None
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(user, pw)
        mail.select('inbox')
        
        status, messages = mail.search(None, 'UNSEEN')
        if status != 'OK' or not messages[0]:
            return ["Nessuna nuova email."]
            
        msg_ids = messages[0].split()[-3:]
        riassunto = []
        
        for msg_id in msg_ids:
            _, data = mail.fetch(msg_id, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            
            soggetto = decodifica_testo(msg.get("Subject", "Senza Oggetto"))
            mittente = pulisci_mittente(decodifica_testo(msg.get("From", "Sconosciuto")))
            riassunto.append(f"• Da: {mittente} | Oggetto: {soggetto}")
            
        return riassunto
    
    except Exception as e:
        return [f"Errore critico accesso mail: {str(e)}"]
    
    finally:
        if mail:
            try:
                mail.logout()
            except:
                pass

def leggi_social():
    """
    Modulo di espansione per Social Media.
    Configura qui le integrazioni (Telegram, WhatsApp, LinkedIn).
    """
    # Esempio: qui potresti richiamare librerie come python-telegram-bot
    return "Modulo Social: Nessuna nuova notifica rilevata dalle API configurate."

def esegui(comando=""):
    """
    Interfaccia pubblica per l'Agente Social Mail.
    """
    cmd = comando.lower().strip()
    
    # 1. GESTIONE MAIL
    if any(p in cmd for p in ["mail", "posta", "email"]):
        risultati = leggi_mail()
        return "Ultime email non lette:\n" + "\n".join(risultati)
        
    # 2. GESTIONE SOCIAL
    if any(p in cmd for p in ["social", "messaggi", "telegram", "whatsapp"]):
        return leggi_social()
        
    # 3. HELP INTERATTIVO
    return (
        "Agente Social Mail operativo.\n"
        "Comandi disponibili:\n"
        "- 'leggi mail' per controllare la posta\n"
        "- 'leggi social' per verificare i messaggi"
    )