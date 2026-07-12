print("IL FILE é PARTITO!")
import asyncio  # <-- CORRETTO: la 'i' deve essere minuscola
import json
import os
import sys

# Gestione robusta dell'importazione di websockets per prevenire SyntaxError su Python 3.14+
try:
    import websockets
except SyntaxError as e:
    print(f"\n[ERRORE DI SINTASSI LIBRERIA]: La versione di 'websockets' installata non è pienamente compatibile con Python {sys.version.split()[0]}.")
    print("Esegui nel terminale: pip install --upgrade --force-reinstall websockets\n")
    sys.exit(1)
except ImportError:
    print("\n[ERRORE]: Libreria 'websockets' mancante. Esegui: pip install websockets\n")
    sys.exit(1)

# Importazione di tutti gli agenti richiesti
import agente_hardware
import agente_informativo
import agente_filosofico
import agente_meteo
import agente_news
import agente_rete
import agente_social_mail
import agente_grafico


class BrainCore:
    def __init__(self):
        self.memory_file = "memoria_personale.json"
        if not os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "w", encoding="utf-8") as f:
                    json.dump([], f)
            except Exception as e:
                print(f"[ERRORE] Creazione file memoria fallita: {e}")

    def salva_in_memoria(self, input_user, risposta_ai):
        try:
            with open(self.memory_file, "r+", encoding="utf-8") as f:
                memoria = json.load(f)
                memoria.append({"input": input_user, "risposta": risposta_ai})
                f.seek(0)
                f.truncate()
                json.dump(memoria, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERRORE] Scrittura memoria fallita: {e}")

    async def monitoraggio_loop(self, websocket):
        """Invia dati di monitoraggio hardware e rete finché la connessione è aperta."""
        try:
            while True:
                # Esecuzione sicura dei controlli di monitoraggio
                try:
                    _, anomalie_hw = agente_hardware.analizza_sistema()
                    cpu_usage = agente_hardware.get_cpu_usage()
                except Exception:
                    anomalie_hw, cpu_usage = [], 0.0

                try:
                    anomalie_rete = agente_rete.controlla_traffico()
                except Exception:
                    anomalie_rete = []

                monitoraggio = {
                    "cpu": cpu_usage,
                    "stato_rete": "OK" if not anomalie_rete else "ALLERTA"
                }

                payload = {
                    "tipo": "MONITOR",
                    "monitoraggio": monitoraggio,
                    "sicurezza": "OPERATIVO"
                }

                # Unione di eventuali anomalie rilevate per notifica POPUP
                tutte_anomalie = anomalie_hw + anomalie_rete
                if tutte_anomalie:
                    payload["tipo"] = "POPUP"
                    payload["contenuto"] = tutte_anomalie[0]

                await websocket.send(json.dumps(payload))
                await asyncio.sleep(30)
        except (websockets.exceptions.ConnectionClosed, asyncio.CancelledError):
            pass  # Chiusura pulita del task di monitoraggio
        except Exception as e:
            print(f"[ERRORE] Loop di monitoraggio: {e}")

    async def process_message(self, message):
        """Elabora i comandi ricevuti dal client e smista ai rispettivi agenti."""
        print(f"\n[DEBUG] Messaggio grezzo arrivato da Flutter: {message}")
        
        try:
            data = json.loads(message)
            comando = data.get("comando_testuale", "").lower().strip()
            print(f"[DEBUG] Comando estratto con successo: '{comando}'")

            # 1. Agente Meteo
            if "meteo" in comando:
                print("[DEBUG] Attivazione Agente Meteo...")
                try:
                    dati = agente_meteo.esegui()
                    return {"tipo": "TABELLA", "contenuto": dati, "sicurezza": "OPERATIVO"}
                except Exception as e:
                    print(f"[ERRORE METEO]: {e}")
                    return {"tipo": "TESTO", "contenuto": f"Errore nell'agente meteo: {e}", "sicurezza": "ERRORE"}

            # 2. Agente News
            elif "news" in comando or "notizie" in comando:
                print("[DEBUG] Attivazione Agente News...")
                try:
                    # Assicurati che la funzione dentro agente_news si chiami così, o cambiala in .esegui()
                    dati = agente_news.ottieni_ultime_notizie() 
                    return {"tipo": "LISTA", "contenuto": dati, "sicurezza": "OPERATIVO"}
                except Exception as e:
                    print(f"[ERRORE NEWS]: {e}")
                    return {"tipo": "TESTO", "contenuto": f"Errore nell'agente news: {e}", "sicurezza": "ERRORE"}

            # 3. Agente Grafico
            elif "grafico" in comando:
                print("[DEBUG] Attivazione Agente Grafico...")
                try:
                    dati = agente_grafico.genera_rappresentazione(comando)
                    return {"tipo": "IMMAGINE", "contenuto": dati, "sicurezza": "OPERATIVO"}
                except Exception as e:
                    print(f"[ERRORE GRAFICO]: {e}")
                    return {"tipo": "TESTO", "contenuto": f"Errore nell'agente grafico: {e}", "sicurezza": "ERRORE"}

            # 4. Modello AI Base (Tutto il resto)
            else:
                print("[DEBUG] Comando generico, passo l'input all'Intelligenza Artificiale...")
                try:
                    import ollama
                    res = ollama.chat(model='llama3', messages=[{'role': 'user', 'content': comando}])
                    risposta = res.get('message', {}).get('content', 'Nessuna risposta dal modello.')
                    
                    # Salva la conversazione per farla imparare
                    self.salva_in_memoria(comando, risposta)
                    print("[DEBUG] Risposta AI generata e salvata in memoria.")
                    
                    return {"tipo": "TESTO", "contenuto": risposta, "sicurezza": "OPERATIVO"}
                except ImportError:
                    print("[DEBUG] Errore: libreria Ollama non installata.")
                    return {"tipo": "TESTO", "contenuto": f"Ho ricevuto: '{comando}'. (Installa la libreria 'ollama' nel server per attivare le risposte AI).", "sicurezza": "OPERATIVO"}
                except Exception as e:
                    print(f"[ERRORE AI]: {e}")
                    return {"tipo": "TESTO", "contenuto": f"Il modello AI è offline o in errore: {e}", "sicurezza": "ERRORE"}

        except Exception as e:
            print(f"[ERRORE FATALE JSON]: Impossibile leggere il messaggio di Flutter: {e}")
            return {"tipo": "ERRORE", "contenuto": "Formato messaggio non valido", "sicurezza": "ERRORE"}         
async def handler(websocket, *args):
    """Gestore della connessione WebSocket."""
    brain = BrainCore()
    monitor_task = asyncio.create_task(brain.monitoraggio_loop(websocket))

    try:
        async for message in websocket:
            response = await brain.process_message(message)
            if response:
                await websocket.send(json.dumps(response, ensure_ascii=False))
    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        print(f"[ERRORE] Gestione connessione client: {e}")
    finally:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


async def main():
    host = "127.0.0.1"
    port = 8080
    print(f"SIA - Sistema Integrato Autonomo Online su ws://{host}:{port}")
    try:
        async with websockets.serve(handler, host, port):
            await asyncio.Future() # <--- QUESTO è il comando che lo tiene acceso all'infinito!
    except OSError as e:
        print(f"\n[ERRORE AVVIO]: Impossibile avviare il server. Porta {port} occupata?")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass