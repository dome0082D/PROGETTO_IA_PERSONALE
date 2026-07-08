import imaplib
import email

def esegui():
    """
    Legge le ultime 3 mail arrivate.
    Nota: Per Gmail, dovrai usare una 'App Password' dalle impostazioni di sicurezza.
    """
    try:
        # Configurazione (Sostituisci con i tuoi dati o usa variabili d'ambiente)
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login('tua_email@gmail.com', 'tua_app_password')
        mail.select('inbox')
        
        status, messages = mail.search(None, 'UNSEEN')
        msg_ids = messages[0].split()[-3:] # Prende le ultime 3 non lette
        
        riassunto = []
        for msg_id in msg_ids:
            res, data = mail.fetch(msg_id, '(RFC822)')
            msg = email.message_from_bytes(data[0][1])
            riassunto.append(f"Da: {msg['from']}, Oggetto: {msg['subject']}")
            
        mail.logout()
        return "Ultime mail: " + " | ".join(riassunto) if riassunto else "Nessuna nuova mail."
    except Exception as e:
        return f"Errore accesso mail: {str(e)}"