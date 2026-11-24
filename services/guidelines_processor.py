import numpy as np
import logging

class GuidelinesProcessor:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    
    def __init__(self, file_handler, text_processor, embedding_service, guidelines_file, embeddings_file):
        self.file_handler = file_handler
        self.text_processor = text_processor
        self.embedding_service = embedding_service
        self.guidelines_file = guidelines_file
        self.embeddings_file = embeddings_file

    def load_or_generate_embeddings(self):
        guidelines_embeddings = self.file_handler.load_json(self.embeddings_file)
        guidelines_text = self.file_handler.read_pdf(self.guidelines_file)
        
        guidelines_tokens = self.text_processor.count_tokens(guidelines_text)
        logging.info(f"Token-Anzahl der gesamten Guidelines: {guidelines_tokens}")

        if not guidelines_embeddings:
            logging.info(f"Verarbeite die Guidelines...")
            guidelines_sections = self.text_processor.split_text(guidelines_text, max_tokens=1000)

            logging.info(f"Erstelle Embeddings für die Guidelines...")
            guidelines_embeddings = {}
            total_embedding_tokens = 0

            for section in guidelines_sections:
                if section.strip():
                    embedding = self.embedding_service.get_embedding(section)
                    if embedding is not None:
                        guidelines_embeddings[section] = {"embedding": embedding, "text": section}
                        total_embedding_tokens += self.text_processor.count_tokens(section)

            logging.info(f"Token-Anzahl für Embedding-Erstellung: {total_embedding_tokens}")
            self.file_handler.save_json(guidelines_embeddings, self.embeddings_file)
        else:
            logging.info("Geladene Guidelines-Embeddings werden verwendet.")
        
        return guidelines_embeddings

    def compute_similarity(self, job_embedding, guidelines_embeddings):
        logging.info("Finde die relevantesten Guidelines...")
        similarities = []
        for section, data in guidelines_embeddings.items():
            if "embedding" in data:
                similarity = np.dot(job_embedding, np.array(data["embedding"])) / (
                    np.linalg.norm(job_embedding) * np.linalg.norm(data["embedding"]))
                similarities.append((section, similarity))
        return similarities