from fastapi import FastAPI, HTTPException, Form, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import logging
import os
import json
import sys
from services.file_handler import FileHandler
from services.text_processor import TextProcessor
from services.embedding_service import EmbeddingService
from services.openai_analyzer import OpenAIAnalyzer
from services.guidelines_processor import GuidelinesProcessor

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# FastAPI-Instanz erstellen
app = FastAPI()

# Statische Dateien einbinden
app.mount("/static", StaticFiles(directory="static"), name="static")

# Standardwerte und Konfiguration
DEFAULT_MODEL = "gpt-4o-mini"
CONFIG_FILE = "config.json"

# Erlaubte Modelle laden
def load_allowed_models():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as file:
                config = json.load(file)
                return config.get("allowed_models", [DEFAULT_MODEL])
        except Exception as e:
            logging.warning(f"Fehler beim Laden der Konfigurationsdatei: {e}")
    return ["gpt-4o", "gpt-4o-mini"]

ALLOWED_MODELS = load_allowed_models()

# API Request Schema
class JobAnalysisRequest(BaseModel):
    job_description_file: str
    prompt_template_file: str
    top_n: int = 3
    show_prompt: bool = False
    show_tokens: bool = True
    disable_gpt: bool = False
    model: str = DEFAULT_MODEL

# Datei-Validierung
def validate_file_exists(file_path):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=400, detail=f"Fehler: Die Datei '{file_path}' existiert nicht.")

# Hauptverarbeitung
def process_request(params: JobAnalysisRequest):
    logging.info(f"Verwendetes Modell: {params.model}")
    if params.model not in ALLOWED_MODELS:
        params.model = DEFAULT_MODEL
        logging.warning(f"Ungültiges Modell. Fallback auf Standardwert '{DEFAULT_MODEL}'.")

    validate_file_exists(params.job_description_file)
    validate_file_exists(params.prompt_template_file)

    file_handler = FileHandler()
    text_processor = TextProcessor()
    embedding_service = EmbeddingService()
    analyzer = OpenAIAnalyzer()

    GUIDELINES_EMBEDDINGS_FILE = "guidelines_embeddings.json"
    guidelines_processor = GuidelinesProcessor(file_handler, text_processor, embedding_service, "guidelines.pdf", GUIDELINES_EMBEDDINGS_FILE)

    job_description_text = file_handler.read_pdf(params.job_description_file)
    if not job_description_text:
        raise HTTPException(status_code=500, detail="Fehler: Die Leistungsbeschreibung konnte nicht extrahiert werden.")

    logging.info("Erstelle Embedding für die Leistungsbeschreibung...")
    job_description_embedding = embedding_service.get_embedding(job_description_text)
    if job_description_embedding is None:
        raise HTTPException(status_code=500, detail="Fehler: Embedding für die Leistungsbeschreibung konnte nicht erstellt werden.")

    guidelines_embeddings = guidelines_processor.load_or_generate_embeddings()
    guideline_similarities = guidelines_processor.compute_similarity(job_description_embedding, guidelines_embeddings)
    top_guidelines = sorted(guideline_similarities, key=lambda x: x[1], reverse=True)[:params.top_n]
    relevant_guidelines_text = [(section, guidelines_embeddings[section]["text"]) for section, _ in top_guidelines]

    prompt = file_handler.read_text_file(params.prompt_template_file).format(
        leitlinien="\n\n".join([f"### {section} ###\n{text}" for section, text in relevant_guidelines_text]),
        beschreibung=job_description_text
    )

    response = {
        "status": "success",
        "prompt": prompt if params.show_prompt else "[Prompt verborgen]",
        "tokens": {
            "job_description": text_processor.count_tokens(job_description_text) if params.show_tokens else None,
            "guidelines": text_processor.count_tokens("\n\n".join([text for _, text in relevant_guidelines_text])) if params.show_tokens else None,
            "prompt": text_processor.count_tokens(prompt) if params.show_tokens else None,
        },
        "gpt_result": None
    }

    if not params.disable_gpt:
        response["gpt_result"] = analyzer.analyze_text(prompt, model=params.model)

    return response

# API Endpoint
@app.post("/run")
async def run_analysis(
    job_description_file: UploadFile = File(...),
    prompt_template_file: UploadFile = File(...),
    top_n: int = Form(3),
    model: str = Form(DEFAULT_MODEL),
    show_prompt: bool = Form(False)
):
    # Speichert die hochgeladenen Dateien temporär
    temp_dir = "/tmp"  # Alternativ einen anderen sicheren Speicherort verwenden
    job_desc_path = os.path.join(temp_dir, job_description_file.filename)
    prompt_template_path = os.path.join(temp_dir, prompt_template_file.filename)

    try:
        with open(job_desc_path, "wb") as f:
            f.write(await job_description_file.read())

        with open(prompt_template_path, "wb") as f:
            f.write(await prompt_template_file.read())
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fehler beim Speichern der Dateien: {e}")

    logging.info(f"Empfangen: {job_desc_path}, {prompt_template_path}, top_n={top_n}, model={model}")

    # Validierung der Datei-Existenz
    if not os.path.exists(job_desc_path) or not os.path.exists(prompt_template_path):
        raise HTTPException(status_code=400, detail="Eine oder beide Dateien konnten nicht gespeichert werden.")

    # API-Request-Objekt mit gespeicherten Dateipfaden erstellen
    request_params = {
        "job_description_file": job_desc_path,
        "prompt_template_file": prompt_template_path,
        "top_n": top_n,
        "model": model,
        "show_prompt": show_prompt
    }

    # Hauptverarbeitung aufrufen
    try:
        result = process_request(JobAnalysisRequest(**request_params))
    except Exception as e:
        logging.error(f"Fehler bei der Verarbeitung: {e}")
        raise HTTPException(status_code=500, detail=f"Fehler bei der Analyse: {str(e)}")

    return result

# Optionale Startseite
@app.get("/")
def home():
    return {"message": "Willkommen zur Guideline Checker API! Besuche /docs für die API-Dokumentation, /ui für die Benutzeroberfläche."}

@app.get("/ui")
def serve_ui():
    return RedirectResponse(url="/static/index.html")

# CLI oder API Starten
if __name__ == "__main__":
    if len(sys.argv) > 1:
        import argparse
        parser = argparse.ArgumentParser(description="Prüfe eine Leistungsbeschreibung anhand der Leitlinien.")
        parser.add_argument("--job_description_file", type=str, required=True)
        parser.add_argument("--prompt_template_file", type=str, required=True)
        parser.add_argument("--top_n", type=int, default=3)
        parser.add_argument("--show_prompt", action="store_true")
        parser.add_argument("--show_tokens", action="store_true")
        parser.add_argument("--disable_gpt", action="store_true")
        parser.add_argument("--model", type=str, default=DEFAULT_MODEL)
        args = parser.parse_args()
        
        request = JobAnalysisRequest(**vars(args))
        result = process_request(request)
        print(json.dumps(result, indent=4, ensure_ascii=False))
    else:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
