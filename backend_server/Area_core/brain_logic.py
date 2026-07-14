# Area_Core/brain_logic.py
import asyncio
import json
import sys
import random
from Area_Core.action_executor import ActionExecutor

# Importazione di tutti gli agenti richiesti dalla cartella Area_Agenti
try:
    from Area_Agenti import agente_filosofico
    from Area_Agenti import agente_grafico
    from Area_Agenti import agente_hardware
    from Area_Agenti import agente_informativo
    from Area_Agenti import agente_meteo
    from Area_Agenti import agente_news
    from Area_Agenti import agente_operativo
    from Area_Agenti import agente_proattivo
    from Area_Agenti import agente_rete
    from Area_Agenti import agente_ricerca
    from Area_Agenti import agente_social_mail
except ImportError as e:
    print(f"[ATTENZIONE] Un agente non è stato trovato nell'Area_Agenti: {e}. Il sistema si avvierà comunque.")

class BrainCore:
    def __init__(self):
        # Inizializza l'esecutore per le operazioni pratiche
        self.executor = ActionExecutor()

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

    async def process_message(self, message):
        """Elabora il messaggio in ingresso (testo o file) e smista il comando ai vari agenti."""
        print(f"\n[DEBUG] Messaggio in arrivo...")
        try:
            data = json.loads(message)
            comando = data.get("comando_testuale", "").lower().strip()
            
            # Predisposizione per la ricezione e l'apprendimento dai file
            if "file_base64" in data or "immagine" in data:
                print("[DEBUG] Ricevuto un file da analizzare.")
                return {"tipo": "TESTO", "contenuto": "File ricevuto correttamente. Modulo di visione e assimilazione in fase di attivazione.", "sicurezza": "OPERATIVO"}
            
            print(f"[DEBUG] Comando estratto: '{comando}'")

            # --- LOGICA DI SMISTAMENTO AGENTI ---
            # Nota: Usiamo la sintassi di sys.modules aggiornata col prefisso del pacchetto
            if "meteo" in comando or "tempo fa" in comando:
                dati = agente_meteo.esegui() if 'Area_Agenti.agente_meteo' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_meteo'], 'esegui') else "Modulo Meteo offline."
                return {"tipo": "TABELLA", "contenuto": dati, "sicurezza": "OPERATIVO"}
            
            elif "news" in comando or "notizie" in comando:
                dati = agente_news.ottieni_ultime_notizie() if 'Area_Agenti.agente_news' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_news'], 'ottieni_ultime_notizie') else "Modulo News offline."
                return {"tipo": "LISTA", "contenuto": dati, "sicurezza": "OPERATIVO"}
            
            elif "grafico" in comando or "disegna" in comando:
                dati = agente_grafico.genera_rappresentazione(comando) if 'Area_Agenti.agente_grafico' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_grafico'], 'genera_rappresentazione') else "Modulo Grafico offline."
                return {"tipo": "IMMAGINE", "contenuto": dati, "sicurezza": "OPERATIVO"}
            
            elif "rete" in comando or "traffico" in comando or "internet" in comando:
                dati = agente_rete.controlla_traffico() if 'Area_Agenti.agente_rete' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_rete'], 'controlla_traffico') else "Modulo Rete offline."
                return {"tipo": "TESTO", "contenuto": f"Analisi traffico: {dati}", "sicurezza": "OPERATIVO"}
            
            elif "mail" in comando or "social" in comando or "posta" in comando:
                dati = agente_social_mail.esegui(comando) if 'Area_Agenti.agente_social_mail' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_social_mail'], 'esegui') else "Modulo Social/Mail offline."
                return {"tipo": "LISTA", "contenuto": dati, "sicurezza": "OPERATIVO"}
            
            elif "operativo" in comando or "sistema" in comando or "gestisci" in comando:
                dati = agente_operativo.esegui(comando) if 'Area_Agenti.agente_operativo' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_operativo'], 'esegui') else "Modulo Operativo offline."
                return {"tipo": "TESTO", "contenuto": dati, "sicurezza": "OPERATIVO"}
            
            elif "proattivo" in comando or "analizza" in comando or "prevedi" in comando:
                dati = agente_proattivo.esegui(comando) if 'Area_Agenti.agente_proattivo' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_proattivo'], 'esegui') else "Modulo Proattivo offline."
                return {"tipo": "TESTO", "contenuto": dati, "sicurezza": "OPERATIVO"}
                
            elif "filosofia" in comando or "pensa" in comando or "senso" in comando:
                dati = agente_filosofico.esegui(comando) if 'Area_Agenti.agente_filosofico' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_filosofico'], 'esegui') else "Modulo Filosofico offline."
                return {"tipo": "TESTO", "contenuto": dati, "sicurezza": "OPERATIVO"}
                
            elif "informazione" in comando or "info" in comando:
                dati = agente_informativo.esegui(comando) if 'Area_Agenti.agente_informativo' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_informativo'], 'esegui') else "Modulo Informativo offline."
                return {"tipo": "TESTO", "contenuto": dati, "sicurezza": "OPERATIVO"}

            else:
                # Se nessun agente specifico viene chiamato, il comando passa al modello LLM generale
                try:
                    import ollama
                    istruzione_sistema = (
                        "Sei SIA, un assistente virtuale iper-intelligente e autonomo. "
                        "Rispondi in modo colloquiale, preciso, conciso e in italiano."
                    )
                    
                    res = await asyncio.to_thread(
                        ollama.chat,
                        model='llama3', 
                        messages=[
                            {'role': 'system', 'content': istruzione_sistema},
                            {'role': 'user', 'content': comando}
                        ]
                    )
                    
                    risposta = res.get('message', {}).get('content', 'Nessuna risposta dal modello.')
                    self.executor.salva_in_memoria(comando, risposta)
                    audio_generato = await self.executor.genera_audio_base64(risposta)
                    
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
                
                # Agente Hardware - Utilizzato passivamente nel loop
                try:
                    if 'Area_Agenti.agente_hardware' in sys.modules and hasattr(sys.modules['Area_Agenti.agente_hardware'], 'get_cpu_usage'):
                        cpu_usage = sys.modules['Area_Agenti.agente_hardware'].get_cpu_usage()
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
                except Exception: # Chiuso
                    break

                # Agente Ricerca - Attivato in modo randomico nel loop (Auto-apprendimento)
                if random.random() < 0.05 and 'Area_Agenti.agente_ricerca' in sys.modules:
                    try:
                        if hasattr(sys.modules['Area_Agenti.agente_ricerca'], 'ricerca_autonoma'):
                            risultati, tema = sys.modules['Area_Agenti.agente_ricerca'].ricerca_autonoma()
                            if risultati:
                                corpo_conoscenza = risultati[0].get('body', 'Dettagli appresi.')
                                if hasattr(sys.modules['Area_Agenti.agente_ricerca'], 'registra_nuova_conoscenza'):
                                    sys.modules['Area_Agenti.agente_ricerca'].registra_nuova_conoscenza(tema, corpo_conoscenza)
                                msg = f"Ho studiato in autonomia: {tema}"
                                await self.invia_popup(websocket, "Auto-Apprendimento", msg)
                    except Exception as re:
                        print(f"[ERRORE APPRENDIMENTO AUTOMATICO]: {re}")

                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"[ERRORE MONITORAGGIO LOOP]: {e}")