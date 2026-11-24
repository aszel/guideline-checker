# Wähle das Basis-Image mit der passenden Python-Version
#FROM python:3.13.1
FROM --platform=linux/amd64 python:3.13.1-slim

# Setze das Arbeitsverzeichnis im Container
WORKDIR /app

# Kopiere die Requirements-Datei und installiere die Abhängigkeiten
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Kopiere den restlichen Code ins Arbeitsverzeichnis
COPY . .

# Standardkommando, um die App zu starten
CMD ["python", "guideline-checker.py"]
