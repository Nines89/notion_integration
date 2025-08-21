import os
import socketserver
import subprocess
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from urllib.parse import unquote


import logging

# Configurazione del logging
logging.basicConfig(
    level=logging.DEBUG,  # Livello minimo di log
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler("app.log"),   # Log su file
    ]
)

logger = logging.getLogger("FileServerLogger")


# Configurazione di base
default_config = {
    "base_dir": r"C:\Users\User\Desktop\notion_integration\pythonApiBath",
    "server_port": 3030,
    "server_host": "http://localhost"
}


def open_explorer(path: str):
    """
    Apre Esplora File sul percorso richiesto dall'utente.
    Il percorso è sempre relativo a base_dir per evitare accessi fuori.
    """
    path = unquote(path)  # Decodifica %20, ecc.
    relative_path = path.lstrip("/")  # Rimuove lo "/" iniziale
    full_path = os.path.join(default_config['base_dir'], relative_path)
    full_path = os.path.normpath(full_path)

    # Sicurezza: impedisce di uscire dalla base_dir
    if not full_path.startswith(default_config['base_dir']):
        logger.info("Accesso negato:", full_path)
        return False

    # Se il percorso non esiste → messaggio di avviso
    if not os.path.exists(full_path):
        logger.info("Percorso non trovato:", full_path)
        return False

    # Apre Esplora File
    subprocess.Popen(['explorer', full_path])
    logger.info("Aperto:", full_path)
    return True


class MyHandler(BaseHTTPRequestHandler):
    """
    Gestore delle richieste HTTP.
    Ogni richiesta GET apre Esplora File sulla cartella/file corrispondente.
    """

    def do_GET(self):
        # Ignora la richiesta del browser per /favicon.ico
        if self.path == "/favicon.ico":
            self.send_response(HTTPStatus.NOT_FOUND)
            self.end_headers()
            return

        # Esegui apertura file/cartella
        success = open_explorer(self.path)

        # Risposta al browser (non apre nulla lì, solo un messaggio)
        if success:
            msg = "File aperto correttamente.".encode("utf-8")
        else:
            msg = "Errore: percorso non valido o inesistente.".encode("utf-8")

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(msg)))
        self.end_headers()
        self.wfile.write(msg)


def start_server():
    """Avvia il server HTTP locale."""
    logger.info(f"Server in ascolto su {default_config['server_host']}:{default_config['server_port']}")
    httpd.serve_forever()


# Creazione del server
httpd = socketserver.TCPServer(("", default_config['server_port']), MyHandler)

# Avvio
if __name__ == "__main__":
    start_server()
