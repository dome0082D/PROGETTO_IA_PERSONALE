# server.py
import asyncio
import json
import os
import sys

# Assicura che il percorso del progetto sia disponibile per l'importazione
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importa il cervello dall'Area Core
try:
    import Area_Core.brain_logic as brain_logic_module
except ImportError:
    import importlib.util

    brain_logic_candidates = [
        os.path.join(project_root, "Area_Core", "brain_logic.py"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "Area_Core", "brain_logic.py"),
    ]
    brain_logic_path = next((path for path in brain_logic_candidates if os.path.exists(path)), None)

    if brain_logic_path is None:
        raise

    spec = importlib.util.spec_from_file_location("Area_Core.brain_logic", brain_logic_path)
    if spec is None or spec.loader is None:
        raise ImportError("Impossibile caricare il modulo Area_Core.brain_logic")

    brain_logic_module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = brain_logic_module
    spec.loader.exec_module(brain_logic_module)

print("IL FILE È PARTITO!")

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

async def handler(websocket):
    """Gestore principale della connessione WebSocket."""
    print("[DEBUG] Connessione in arrivo dal client...")
    
    # Inizializza il cervello per questa sessione
    brain = Area_Core.brain_logic.BrainCore()
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
            await asyncio.Future()
    except OSError as e:
        print(f"\n[ERRORE AVVIO]: Porta {port} occupata o irraggiungibile. {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[CHIUSURA] SIA terminato manualmente. Arrivederci!")