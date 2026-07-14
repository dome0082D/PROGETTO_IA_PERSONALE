import subprocess
import os

def disinstalla_programma(nome_processo):
    """
    Chiude forzatamente un processo che rallenta il PC (su Windows).
    Il nome originale 'disinstalla_programma' è mantenuto, ma l'azione è un 'Taskkill'.
    """
    try:
        # Aggiunto capture_output per intercettare le risposte di Windows senza sporcare il terminale
        risultato = subprocess.run(
            f"taskkill /F /IM {nome_processo}.exe", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        
        # Controllo se l'operazione è andata a buon fine (returncode 0 significa SUCCESSO)
        if risultato.returncode == 0:
            return f"Processo {nome_processo} terminato con successo. Risorse liberate."
        else:
            # Se il processo non esiste o c'è un errore, riportiamo il messaggio pulito
            errore = risultato.stderr.strip() or "Processo non trovato o già chiuso."
            return f"Impossibile terminare {nome_processo}: {errore}"
            
    except Exception as e:
        return f"Errore critico durante la chiusura del processo: {e}"


# --- INTERFACCIA PER IL NUOVO LOADER MODULARE ---
def esegui(comando=""):
    """
    Funzione standard di interfaccia. 
    Analizza il comando e capisce quale programma l'utente vuole chiudere.
    """
    cmd = comando.lower().strip()
    
    # Cerca la parola chiave e isola il nome del programma
    parole = cmd.split()
    nome_processo = ""
    
    # Parole chiave che attivano l'agente
    for keyword in ["chiudi", "termina", "stoppa", "killa", "disinstalla"]:
        if keyword in parole:
            idx = parole.index(keyword)
            # Prende la parola successiva come nome del processo
            if idx + 1 < len(parole):
                nome_processo = parole[idx + 1].replace(".exe", "") # Pulisce eventuali .exe scritti dall'utente
                break
                
    # Se ha trovato un bersaglio, lancia il tuo comando
    if nome_processo:
        return disinstalla_programma(nome_processo)
        
    return "Specifica il nome del programma da chiudere (es: 'SIA, chiudi chrome')."