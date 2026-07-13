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
import agente_ricerca


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
        """Trasforma il testo in un file audio con voce femminile naturale (ChiaraNeural)."""
        try:
            import edge_tts 
            import base64
            
            # Voce femminile naturale, fluida e con intonazione umana avanzata
            VOICE = "it-IT-ChiaraNeural"
            
            communicate = edge_tts.Communicate(testo_da_pronunciare, VOICE)
            audio_bytes = b""
            
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_bytes += chunk["data"]
            
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            return audio_base64
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
        await websocket.send(json.dumps(notifica, ensure_ascii=False))

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


async def handler(websocket):
    """Semplice handler WebSocket di fallback: logga e risponde a messaggi di testo."""
    try:
        async for message in websocket:
            # Risposta di base; l'app può inviare comandi JSON e gestirli altrove
            try:
                data = json.loads(message)
            except Exception:
                data = {"raw": message}
            response = {"status": "ok", "received": data}
            await websocket.send(json.dumps(response, ensure_ascii=False))
    except websockets.exceptions.ConnectionClosed:
        return


async def main():
    host = "0.0.0.0"
    port = 8080
    print(f"SIA - Sistema Integrato Autonomo Online su ws://{host}:{port}")
    try:
        async with websockets.serve(handler, host, port):
            await asyncio.Future()
    except OSError as e:
        print(f"\n[ERRORE AVVIO]: Impossibile avviare il server. Porta {port} occupata? {e}")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[CHIUSURA] Server SIA terminato manualmente. Arrivederci!")            