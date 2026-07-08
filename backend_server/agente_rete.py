import psutil
import speedtest # Richiede: pip install speedtest-cli
import time

def monitora_rete():
    # 1. Controllo base: Stato dell'interfaccia
    connessioni = psutil.net_if_stats()
    # 2. Controllo qualità: Latenza e banda (opzionale, esegue un test veloce)
    st = speedtest.Speedtest(secure=True)
    download_speed = st.download() / 1_000_000 # Mbps
    ping = st.results.ping
    
    report = f"Stato Rete: Ping {ping}ms, Download {download_speed:.2f} Mbps."
    
    anomalie = []
    if ping > 100:
        anomalie.append("Latenza elevata: potresti riscontrare lag.")
    if download_speed < 5:
        anomalie.append("Velocità internet critica.")
        
    return report, anomalie