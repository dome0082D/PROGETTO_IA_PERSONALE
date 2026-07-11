import asyncio
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
        try:
            data = json.loads(message)
            comando = data.get("comando_testuale", "").lower().strip()

            # 1. Logica Agente Meteo (Esecuzione preferenziale sul nuovo modulo dedicato)
            if "meteo" in comando:
                try:
                    dati_meteo = agente_meteo.ottieni_previsioni()
                    return {"tipo": "TABELLA", "contenuto": dati_meteo, "sicurezza": "OPERATIVO"}
                except Exception:
                    pass
        except Exception as e:
            print(f"[ERRORE] Elaborazione messaggio: {e}")
            return {"tipo": "ERRORE", "contenuto": "Errore interno", "sicurezza": "ERRORE"}