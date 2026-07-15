# Area_Core/action_executor.py
import json
import os
import base64
import importlib
import re # Aggiunto per pulizia testo più avanzata

class ActionExecutor:
    def __init__(self):
        self.memory_file = "memoria_personale.json"
        if not os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "w", encoding="utf-8") as f:
                    json.dump([], f)
            except Exception as e:
                print(f"[ERRORE] Creazione file memoria fallita: {e}")

    def salva_in_memoria(self, input_user, risposta_ai):
        """Salvataggio robusto: se il file è corrotto, lo resetta senza far crashare il server."""
        memoria = []
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    memoria = json.load(f)
                    if not isinstance(memoria, list):
                        memoria = []
            except (json.JSONDecodeError, ValueError):
                print(f"[AVVISO] Il file {self.memory_file} era corrotto. Ripartiamo da una memoria pulita.")
                memoria = []

        memoria.append({"input": input_user, "risposta": risposta_ai})

        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(memoria, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"[ERRORE] Scrittura memoria fallita: {e}")

    async def genera_audio_base64(self, testo_da_pronunciare):
        """Trasforma il testo in un file audio pulito con voce neurale ad alta qualità."""
        if not testo_da_pronunciare:
            print("[DEBUG] Testo vuoto in ingresso. Nessun audio generato.")
            return None

        try:
            import edge_tts 
            
            # ElsaNeural è considerata una delle voci italiane più naturali e fluide in assoluto.
            # In alternativa, puoi rimettere "it-IT-ChiaraNeural"
            VOICE = "it-IT-ElsaNeural" 
            
            # Pulizia avanzata della formattazione
            testo_pulito = (
                testo_da_pronunciare
                .replace("**", "")
                .replace("*", "")
                .replace("#", "")
                .replace("`", "")
            )
            
            # Rimuove le note di pronuncia tra parentesi (es: "(pronuncia "see-ah")")
            # che l'intelligenza artificiale tenderebbe a leggere letteralmente, sembrando robotica.
            testo_pulito = re.sub(r'\(pronuncia.*?\)', '', testo_pulito, flags=re.IGNORECASE)
            
            testo_pulito = testo_pulito.strip()
            
            if not testo_pulito:
                return None
                
            # Il parametro rate="+15%" velocizza la parlata rendendola molto più umana e meno cantilenante.
            communicate = edge_tts.Communicate(testo_pulito, VOICE, rate="+15%")
            audio_bytes = b""
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            
            print("[DEBUG] Audio neurale generato con successo tramite edge-tts.")
            return base64.b64encode(audio_bytes).decode('utf-8')
            
        except ImportError:
            print("[ERRORE CRITICO] Modulo 'edge_tts' mancante. Python non può generare l'audio e l'app usa la voce robotica di riserva!")
            print("-> RISOLVI DIGITANDO NEL TERMINALE: pip install edge-tts")
            return None
        except Exception as e:
            print(f"[ERRORE SINTESI VOCALE]: {e}")
            return None

    def integra_nuovo_agente(self, nome_agente, nuovo_codice):
        """Aggiunge o estende un agente senza mai sovrascrivere o cancellare i file core (Append-Only)."""
        file_protetti = ["backend_core.py", "agente_hardware.py", "agente_rete.py"]
        if f"{nome_agente}.py" in file_protetti or nome_agente in file_protetti:
            return "Errore: Operazione non consentita su file di sistema protetti."
        
        nome_file = f"Area_Agenti/agente_{nome_agente}.py" if not nome_agente.startswith("agente_") else f"Area_Agenti/{nome_agente}.py"
        
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