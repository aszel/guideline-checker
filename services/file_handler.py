import os
import json
from PyPDF2 import PdfReader

class FileHandler:
    """Kapselt Dateioperationen wie Lesen, Schreiben und Laden von JSON."""
    
    def read_pdf(self, file_path):
        """Liest eine PDF-Datei und gibt den extrahierten Text zurück."""
        try:
            reader = PdfReader(file_path)
            text = "\n".join(page.extract_text() or "" for page in reader.pages).strip()
            return text
        except Exception as e:
            print(f"Fehler beim Lesen der PDF {file_path}: {e}")
            return ""

    def read_text_file(self, file_path):
        """Liest eine normale Textdatei ein und gibt den Inhalt als String zurück."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read().strip()
        except Exception as e:
            print(f"Fehler beim Lesen der Textdatei {file_path}: {e}")
            return ""

    def save_json(self, data, filename):
        """Speichert Daten als JSON-Datei."""
        with open(filename, 'w') as f:
            json.dump(data, f)

    def load_json(self, filename):
        """Lädt Daten aus einer JSON-Datei, falls sie existiert."""
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
        return {}
