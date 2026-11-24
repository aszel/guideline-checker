# README

## Vorraussetzungen

Zur Verwendung der Skripte muss ein gültiger API-KEY für OpenAI unter dem Namen "OPENAI-API-KEY" als Umgebungsvariable vorhanden sein.

## Beschreibung

Der 'guideline-checker' kann als command line tool oder als app mit user-interface genutzt werden.

Er liest 3 Dokumente ein:

* guidelines.pdf (gesetzt)
* job_description.pdf (per Parameter übergeben)
* prompt_template.txt (per Parameter übergeben)

Zur Optimierung der Abfrage an die API werden embeddings aus den guidelines und der job_description erstellt.
Damit wird eine Ähnlichkeitsprüfung (mittels cosine similarity) durchgeführt um nur die relevantesten Teile der guidelines für die Abfrage zu verwenden (Token-Reduzierung). Die Anzahl der relevantesten Teile kann mit Parameter `top_n` gesteuert werden.

Durch die Optimierung konnte eine Reduzierung der request-token von ca. 70% erreicht werden.

## Einschränkungen

Die job_description ist als pdf-Dokument zu übergeben. Das prompt_template muss eine Text-Datei sein und muss bestimmte Vorraussetzungen erfüllen (siehe unten).

Aktuell wird nur die Verwendung der API von OpenAI angeboten:

- https://api.openai.com/v1/embeddings 
- https://api.openai.com/v1/chat/completions

Das verwendete Standart-Model ist `gpt-4o-mini`. Mögliche Optionen sind gpt-4o, gpt-4o-mini, o1-mini, o3-mini (siehe config.json)

Für die Berechnung der embeddings wird das Model `text-embedding-ada-002` verwendet. Es gibt inzwischen ein verbessertes Model.

## Verwendung

Vor dem ersten Start sind die benötigten packages zu installieren

    pip install -r requirements.txt

### Starten mit Docker

    docker run --rm -it -e OPENAI_API_KEY=$OPENAI_API_KEY -p 8000:8000 guideline-checker

### Benutzung als CLI-Tool

Ausführen mit den gegebenen Dokumenten

    python guideline-checker.py --job_description_file job_description.pdf --prompt_template_file prompt_template.txt 

Hilfe anzeigen

    python guideline-checker.py -h
    options:
    -h, --help            show this help message and exit
    --job_description_file JOB_DESCRIPTION_FILE
                            Pfad zur Job Description PDF-Datei
    --prompt_template_file PROMPT_TEMPLATE_FILE
                            Pfad zur Textdatei mit dem Prompt-Template
    --top_n TOP_N         Anzahl der relevantesten Guidelines-Abschnitte, die in den Prompt aufgenommen werden
    --show-prompt         Zeigt den generierten Prompt an
    --show-tokens         Zeigt die Token-Anzahl der verschiedenen Teile des Prozesses an
    --disable-gpt         Deaktiviert die GPT-Analyse
    --model MODEL         Wähle ein Modell (gpt-4o, gpt-4o-mini, o1-mini, o3-mini)

### Benutzung mit user-interface

Starten der App

    python guideline-checker.py

Folgende Adressen werden bereitgestellt: 

* http://127.0.0.1:8000/ - home
* http://127.0.0.1:8000/docs - Swagger UI
* http://127.0.0.1:8000/ui - user interface

## Prompt

Im enthaltenen Dokument `prompt_template.txt` ist das Prompt enthalten.
Bei der Erstellung eines neuen Prompts ist zu beachten, dass folgende Platzhalter im Prompt enhalten sein müssen:

- {leitlinien}
- {beschreibung}