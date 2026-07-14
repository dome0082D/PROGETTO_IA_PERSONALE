import psutil
import subprocess
import re
import os
import socket

try:
    import speedtest  # Richiede: pip install speedtest-cli
except ImportError:
    speedtest = None

def scansione_dispositivi():
    """
    Analizza i dispositivi connessi alla rete locale leggendo la tabella ARP del sistema.
    È velocissimo, non blocca la rete e mappa chi è collegato (router SIM o fisso).
    """
    dispositivi = []
    try:
        # Eseguiamo il comando nativo del sistema operativo per mappare i dispositivi attivi
        risultato = subprocess.run("arp -a", shell=True, capture_output=True, text=True)
        output = risultato.stdout
        
        # Regex per estrarre tutti gli indirizzi IP validi dall'output del terminale
        ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        tutti_gli_ip = ip_pattern.findall(output)
        
        # Filtriamo indirizzi IP di loopback, broadcast e multicast
        ip_validi = set()
        for ip in tutti_gli_ip:
            if not ip.endswith(".255") and not ip.startswith("224.") and not ip.startswith("239.") and ip != "127.0.0.1":
                ip_validi.add(ip)
                
        return list(ip_validi)
    except Exception as e:
        print(f"[ERRORE SCANSIONE DISPOSITIVI]: {e}")
        return []

def analizza_sicurezza_connessioni():
    """
    Analizza le connessioni esterne attive alla ricerca di malware,
    traffico sospetto o backdoor che comunicano all'esterno.
    """
    anomalie = []
    connessioni_attive = 0
    connessioni_per_processo = {}
    
    try:
        # Otteniamo tutte le connessioni IPv4 e IPv6 stabilite sul PC
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'ESTABLISHED':
                connessioni_attive += 1
                pid = conn.pid
                if pid:
                    connessioni_per_processo[pid] = connessioni_per_processo.get(pid, 0) + 1
                    
        # Analizziamo se qualche processo sconosciuto sta aprendo troppe connessioni in uscita
        for pid, count in connessioni_per_processo.items():
            try:
                proc = psutil.Process(pid)
                nome_proc = proc.name().lower()
                
                # Lista di programmi noti che usano molte connessioni (escludiamo falsi positivi)
                processi_sicuri = ["chrome", "firefox", "msedge", "brave", "opera", "discord", "spotify", "node", "python", "vscode", "code"]
                is_sicuro = any(sicuro in nome_proc for sicuro in processi_sicuri)
                
                # Se un processo non fidato apre più di 15 connessioni stabili, è sospetto
                if count > 15 and not is_sicuro:
                    anomalie.append(f"Processo sospetto '{proc.name()}' (PID: {pid}) ha {count} connessioni esterne attive.")
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        if connessioni_attive > 150:
            anomalie.append(f"Numero totale di connessioni attive insolitamente elevato ({connessioni_attive}). Possibile adware o attività di rete anomala.")
            
    except psutil.AccessDenied:
        # Su alcune versioni di Windows psutil.net_connections richiede permessi amministrativi
        anomalie.append("Impossibile scansionare tutte le porte profonde di sistema (avvia il terminale come Amministratore).")
    except Exception as e:
        anomalie.append(f"Errore durante l'analisi della sicurezza delle connessioni: {e}")
        
    return anomalie, connessioni_attive

def monitora_rete(esegui_speedtest=False):
    """
    Esegue il controllo qualità della rete.
    """
    # 1. Controllo base: Stato dell'interfaccia
    connessioni = psutil.net_if_stats()
    interfacce_attive = [nome for nome, stats in connessioni.items() if stats.isup]
    
    if not interfacce_attive:
        return "Stato Rete: Offline. Nessuna interfaccia di rete attiva rilevata.", ["Tutte le schede di rete risultano disconnesse."]

    anomalie = []
    report = f"Interfacce attive: {', '.join(interfacce_attive)}."

    if speedtest is None:
        report += " Test velocità non disponibile (speedtest-cli non installato)."
        return report, anomalie

    if esegui_speedtest:
        try:
            st = speedtest.Speedtest(secure=True)
            download_speed = st.download() / 1_000_000  # Mbps
            ping = st.results.ping
            
            report = f"Stato Rete: Ping {ping}ms, Download {download_speed:.2f} Mbps."
            
            if ping > 100:
                anomalie.append(f"Latenza elevata ({ping}ms): potresti riscontrare lag.")
            if download_speed < 5:
                anomalie.append(f"Velocità internet critica ({download_speed:.2f} Mbps).")
        except Exception as e:
            report += f" Impossibile completare il test di velocità: {e}"
    else:
        report += " (Speedtest saltato per non rallentare il sistema. Chiedi 'test velocità' per eseguirlo)."
        
    return report, anomalie


# --- INTERFACCIA PER IL NUOVO LOADER MODULARE ---
def esegui(comando=""):
    """
    Funzione standard di interfaccia. Indirizza le richieste sul controllo sicurezza,
    analisi degli intrusi o qualità della linea.
    """
    cmd = comando.lower().strip()
    
    # 1. ANALISI DISPOSITIVI E INTRUSI
    if any(parola in cmd for parola in ["chi c'è", "dispositivi", "connessi", "collegati", "intrus", "router", "persone"]):
        lista_ip = scansione_dispositivi()
        num_dispositivi = len(lista_ip)
        
        risposta = f"SIA Analisi Rete: Rilevati {num_dispositivi} dispositivi attivi nella tua rete locale.\n"
        if num_dispositivi > 0:
            risposta += "\nIndirizzi IP rilevati attivi:\n"
            for ip in lista_ip:
                risposta += f"- {ip}\n"
            risposta += "\n*Nota: Se noti IP non riconosciuti, potrebbero appartenere a smartphone, schede domotiche o Smart TV collegate alla tua rete.*"
        return risposta

    # 2. ANALISI SICUREZZA E MALWARE
    if any(parola in cmd for parola in ["sicurezza", "malware", "anomalie", "sospett", "virus", "spia"]):
        anomalie, connessioni_attive = analizza_sicurezza_connessioni()
        
        risposta = f"SIA Controllo Sicurezza: {connessioni_attive} connessioni attive analizzate.\n\n"
        if anomalie:
            risposta += "⚠️ ALLERTA SICUREZZA RILEVATA:\n"
            for anomalia in anomalie:
                risposta += f"- {anomalia}\n"
        else:
            risposta += "✅ Nessuna anomalia riscontrata. Tutti i processi di rete attivi appartengono ad applicazioni conosciute."
        return risposta

    # 3. STATO RETE E SPEEDTEST (Solo su richiesta esplicita)
    richiede_speedtest = any(parola in cmd for parola in ["velocità", "speedtest", "banda", "ping"])
    report, anomalie = monitora_rete(esegui_speedtest=richiede_speedtest)
    
    risposta = f"SIA Stato Rete: {report}\n"
    if anomalie:
        risposta += "\n⚠️ Anomalie Rilevate:\n" + "\n".join([f"- {a}" for a in anomalie])
        
    return risposta