import numpy as np
import openai

client = openai.OpenAI()

class EmbeddingService:
    """Verantwortlich für die Erstellung und Verarbeitung von Embeddings."""

    def get_embedding(self, text):
        try:
            response = client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"Fehler beim Erstellen des Embeddings: {e}")
            return None

    def get_relevant_guidelines(self, job_embedding, guidelines_embeddings, top_n=3):
        similarities = [
            (section, np.dot(job_embedding, np.array(embedding)) /
             (np.linalg.norm(job_embedding) * np.linalg.norm(embedding)))
            for section, embedding in guidelines_embeddings.items() if embedding is not None
        ]
        similarities.sort(key=lambda x: x[1], reverse=True)
        return [section for section, _ in similarities[:top_n]]
