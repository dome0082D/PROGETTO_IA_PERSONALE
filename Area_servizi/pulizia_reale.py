import os
import shutil

def pulisci_file_temporanei():
    # Percorsi reali di sistema dove si annida la spazzatura
    percorsi = [os.environ.get('TEMP'), 'C:/Windows/Temp']
    count = 0
    for p in percorsi:
        if p and os.path.exists(p):
            for f in os.listdir(p):
                try:
                    path = os.path.join(p, f)
                    if os.path.isfile(path): os.remove(path)
                    count += 1
                except: continue
    return f"Pulizia eseguita: rimossi {count} file inutili."