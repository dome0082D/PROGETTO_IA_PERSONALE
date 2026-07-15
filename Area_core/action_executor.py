# Area_Core/action_executor.py
import json
import os
import base64
import importlib
import re

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

    def carica_memoria(self):
        """Legge l'intero storico dal file JSON. Usata all'avvio per ricaricare tutta la conversazione visiva."""
        if not os.path.exists(self.memory_file):
            return []
        try:
            with open(self.memory_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception as e:
            print(f"[ERRORE] Caricamento memoria fallito: {e}")
            return []

    def get_history_for_llm(self, limit=40):
        """
        Formatta la memoria per l'IA. 
        Prende gli ultimi 40 messaggi per garantire una memoria solida senza sovraccaricare la CPU.
        """
        history = []
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    recent_data = data[-limit:] if isinstance(data, list) else []
                    
                    for entry in recent_data:
                        history.append({'role': 'user', 'content': entry.get('input', '')})
                        history.append({'role': 'assistant', 'content': entry.get('risposta', '')})
            except Exception as e:
                print(f"[ERRORE] Lettura memoria per LLM: {e}")
        return history

    async def genera_audio_base64(self, testo_da_pronunciare):
        """Trasforma il testo in audio neurale. Nessun parametro 'rate' per evitare l'errore del server Microsoft."""
        if not testo_da_pronunciare:
            return None

        try:
            import edge_tts
            
            # Pulizia profonda del testo per evitare errori del motore TTS (suoni metallici)
            testo_pulito = re.sub(r'[\*\#\`]', '', testo_da_pronunciare)
            testo_pulito = re.sub(r'\(.*?\)', '', testo_pulito)
            testo_pulito = re.sub(r'[^\w\s\.\,\!\?]', '', testo_pulito)
            testo_pulito = testo_pulito.strip()

            if not testo_pulito:
                return None
            
            # Voce stabile Isabella. Zero parametri extra.
            VOICE = "it-IT-IsabellaNeural"
            communicate = edge_tts.Communicate(testo_pulito, VOICE)
            
            audio_bytes = b""
            # Raccolta stream audio
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            
            # CONTROLLO INTEGRITÀ
            if len(audio_bytes) < 100: 
                print("[ERRORE SINTESI VOCALE]: Dati audio troppo brevi o assenti (possibile blocco Microsoft).")
                return None
            
            return base64.b64encode(audio_bytes).decode('utf-8')
            
        except ImportError:
            print("[ERRORE CRITICO] Libreria 'edge_tts' non trovata.")
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