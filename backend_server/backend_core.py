print("IL FILE È PARTITO!")
import asyncio
import json
import os
import sys
import base64
import random
import importlib

# Gestione robusta dell'importazione di websockets
try:
    import websockets
except SyntaxError as e:
    print(f"\n[ERRORE DI SINTASSI LIBRERIA]: La versione di 'websockets' installata non è pienamente compatibile.")
    print("Esegui nel terminale: pip install --upgrade --force-reinstall websockets\n")
    sys.exit(1)
except ImportError:
    print("\n[ERRORE]: Libreria 'websockets' mancante. Esegui: pip install websockets\n")
    sys.exit(1)

# Importazione di tutti gli agenti richiesti
try:
    import agente_hardware
    import agente_informativo
    import agente_filosofico
    import agente_meteo
    import agente_news
    import agente_rete
    import agente_social_mail
    import agente_grafico
    import agente_ricerca
except ImportError as e:
    print(f"[ATTENZIONE] Un agente non è stato trovato: {e}. Il sistema si avvierà comunque.")

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

    async def genera_audio_base64(self, testo_da_pronunciare):
        """Trasforma il testo in un file audio pulito con voce ChiaraNeural, senza markdown."""
        try:
            import edge_tts 
            VOICE = "it-IT-ChiaraNeural"
            
            # Pulizia profonda dai caratteri di formattazione Markdown che bloccano la sintesi vocale
            testo_pulito = (
                testo_da_pronunciare
                .replace("**", "")
                .replace("*", "")
                .replace("#", "")
                .replace("`", "")
                .strip()
            )
            
            if not testo_pulito:
                print("[DEBUG] Testo vuoto dopo la pulizia. Nessun audio generato.")
                return None
                
            communicate = edge_tts.Communicate(testo_pulito, VOICE)
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            return base64.b64encode(audio_bytes).decode('utf-8')
        except ImportError:
            print("[ATTENZIONE] Modulo 'edge_tts' mancante. Audio non generato.")
            return None
        except Exception as e:
            print(f"[ERRORE SINTESI VOCALE]: {e}")
            return None

    async def invia_popup(self, websocket, titolo, messaggio):
        """Invia un pacchetto strutturato che l'app Flutter interpreterà come pop-up proattivo."""
        notifica = {
            "tipo": "POPUP",
            "titolo": titolo,
            "messaggio": messaggio,
            "sicurezza": "PROATTIVO"
        }
        try:
            await websocket.send(json.dumps(notifica, ensure_ascii=False))
        except Exception as e:
            print(f"[ERRORE INVIO POPUP]: {e}")

    def integra_nuovo_agente(self, nome_agente, nuovo_codice):
        """Aggiunge o estende un agente senza mai sovrascrivere o cancellare i file core (Append-Only)."""
        file_protetti = ["backend_core.py", "agente_hardware.py", "agente_rete.py"]
        if f"{nome_agente}.py" in file_protetti or nome_agente in file_protetti:
            return "Errore: Operazione non consentita su file di sistema protetti."
        
        nome_file = f"agente_{nome_agente}.py" if not nome_agente.startswith("agente_") else f"{nome_agente}.py"
        
        try:
            if os.path.exists(nome_file):
                with open(nome_file, "a", encoding="utf-8") as f:
                    f.write(f"\n\n# --- AGGIORNAMENTO AUTOMATICO --- \n{nuovo_codice}")
                importlib.invalidate_caches()
                return f"Agente {nome_agente} esteso con successo tramite logica protetta."
            else:
                with open(nome_file, "w", encoding="utf-8") as f:
                    f.write(nuovo_codice)
                importlib.invalidate_caches()
                return f"Nuovo agente {nome_file} creato"
        except Exception as e:
            print(f"[ERRORE] Integrazione agente fallita: {e}")
            return f"Errore: {e}"

    async def process_message(self, message):
        """Elabora il messaggio in ingresso (testo o file) e smista il comando."""
        print(f"\n[DEBUG] Messaggio in arrivo...")
        try:
            data = json.loads(message)
            comando = data.get("comando_testuale", "").lower().strip()
            
            # Predisposizione per la ricezione e l'apprendimento dai file (es. orari di lavoro)
            if "file_base64" in data or "immagine" in data:
                print("[DEBUG] Ricevuto un file da analizzare.")
                return {"tipo": "TESTO", "contenuto": "File ricevuto correttamente. Modulo di visione e assimilazione in fase di attivazione.", "sicurezza": "OPERATIVO"}
            
            print(f"[DEBUG] Comando estratto: '{comando}'")

            if "meteo" in comando:
                dati = agente_meteo.esegui() if 'agente_meteo' in sys.modules and hasattr(sys.modules['agente_meteo'], 'esegui') else "Modulo Meteo offline."
                return {"tipo": "TABELLA", "contenuto": dati, "sicurezza": "OPERATIVO"}
            elif "news" in comando or "notizie" in comando:
                dati = agente_news.ottieni_ultime_notizie() if 'agente_news' in sys.modules and hasattr(sys.modules['agente_news'], 'ottieni_ultime_notizie') else "Modulo News offline."
                return {"tipo": "LISTA", "contenuto": dati, "sicurezza": "OPERATIVO"}
            elif "grafico" in comando:
                dati = agente_grafico.genera_rappresentazione(comando) if 'agente_grafico' in sys.modules and hasattr(sys.modules['agente_grafico'], 'genera_rappresentazione') else "Modulo Grafico offline."
                return {"tipo": "IMMAGINE", "contenuto": dati, "sicurezza": "OPERATIVO"}
            elif "rete" in comando or "traffico" in comando:
                dati = agente_rete.controlla_traffico() if 'agente_rete' in sys.modules and hasattr(sys.modules['agente_rete'], 'controlla_traffico') else "Modulo Rete offline."
                return {"tipo": "TESTO", "contenuto": f"Analisi traffico: {dati}", "sicurezza": "OPERATIVO"}
            else:
                try:
                    import ollama
                    istruzione_sistema = (
                        "Sei SIA, un assistente virtuale iper-intelligente e autonomo. "
                        "Rispondi in modo colloquiale, preciso, conciso e in italiano."
                    )
                    
                    # Esecuzione in thread separato asincrono per evitare freeze di CPU e monitoraggio
                    res = await asyncio.to_thread(
                        ollama.chat,
                        model='llama3', 
                        messages=[
                            {'role': 'system', 'content': istruzione_sistema},
                            {'role': 'user', 'content': comando}
                        ]
                    )
                    
                    risposta = res.get('message', {}).get('content', 'Nessuna risposta dal modello.')
                    self.salva_in_memoria(comando, risposta)
                    audio_generato = await self.genera_audio_base64(risposta)
                    
                    return {
                        "tipo": "TESTO", 
                        "contenuto": risposta, 
                        "audio": audio_generato,
                        "sicurezza": "OPERATIVO"
                    }
                except ImportError:
                    return {"tipo": "TESTO", "contenuto": f"Ricevuto: '{comando}'. (Installa 'ollama').", "sicurezza": "OPERATIVO"}
                except Exception as e:
                    return {"tipo": "TESTO", "contenuto": f"AI offline: {e}", "sicurezza": "ERRORE"}
        except Exception as e:
            return {"tipo": "ERRORE", "contenuto": f"Formato dati non valido: {e}", "sicurezza": "ERRORE"}

    async def monitoraggio_loop(self, websocket):
        """Ciclo vitale in background di SIA per monitoraggio e apprendimento continuo."""
        try:
            while True:
                cpu_usage = 0.0
                anomalie_rete = []
                
                try:
                    if 'agente_hardware' in sys.modules and hasattr(sys.modules['agente_hardware'], 'get_cpu_usage'):
                        cpu_usage = sys.modules['agente_hardware'].get_cpu_usage()
                except Exception:
                    pass

                monitoraggio = {
                    "cpu": cpu_usage,
                    "stato_rete": "OK" if not anomalie_rete else "ALLERTA"
                }

                payload = {
                    "tipo": "MONITOR",
                    "monitoraggio": monitoraggio,
                    "sicurezza": "OPERATIVO"
                }

                try:
                    await websocket.send(json.dumps(payload, ensure_ascii=False))
                except websockets.exceptions.ConnectionClosed:
                    break

                # Piccola possibilità di fare ricerca autonoma ogni 30 secondi
                if random.random() < 0.05 and 'agente_ricerca' in sys.modules:
                    try:
                        if hasattr(sys.modules['agente_ricerca'], 'ricerca_autonoma'):
                            risultati, tema = sys.modules['agente_ricerca'].ricerca_autonoma()
                            if risultati:
                                corpo_conoscenza = risultati[0].get('body', 'Dettagli appresi.')
                                if hasattr(sys.modules['agente_ricerca'], 'registra_nuova_conoscenza'):
                                    sys.modules['agente_ricerca'].registra_nuova_conoscenza(tema, corpo_conoscenza)
                                msg = f"Ho studiato in autonomia: {tema}"
                                await self.invia_popup(websocket, "Auto-Apprendimento", msg)
                    except Exception as re:
                        print(f"[ERRORE APPRENDIMENTO AUTOMATICO]: {re}")

                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[ERRORE MONITORAGGIO LOOP]: {e}")


async def handler(websocket):
    """Gestore principale della connessione WebSocket."""
    print("[DEBUG] Connessione in arrivo dal client...")
    brain = BrainCore()
    monitor_task = asyncio.create_task(brain.monitoraggio_loop(websocket))

    try:
        async for message in websocket:
            print(f"[DEBUG] Interazione ricevuta.")
            response = await brain.process_message(message)
            if response:
                await websocket.send(json.dumps(response, ensure_ascii=False))
    except websockets.exceptions.ConnectionClosed:
        print("[DEBUG] Client disconnesso.")
    except Exception as e:
        print(f"[ERRORE] Handler principale: {e}")
    finally:
        monitor_task.cancel()
        try:
            await monitor_task
        except asyncio.CancelledError:
            pass


async def main():
    host = "0.0.0.0"
    port = 8080
    print(f"SIA - Sistema Integrato Autonomo Online su ws://{host}:{port}")
    try:
        async with websockets.serve(handler, host, port):
            # Questo comando mantiene in vita il server indefinitamente
            await asyncio.Future()
    except OSError as e:
        print(f"\n[ERRORE AVVIO]: Porta {port} occupata o irraggiungibile. {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[CHIUSURA] SIA terminato manualmente. Arrivederci!")