import tiktoken

TOKEN_LIMIT = 8192  # OpenAI Embedding-Modell-Limit

class TextProcessor:
    """Bietet Methoden zur Token-Zählung und Textaufteilung."""

    def count_tokens(self, text):
        encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def split_text(self, text, max_tokens=TOKEN_LIMIT - 500):
        words = text.split()
        chunks, current_chunk, current_tokens = [], [], 0

        for word in words:
            word_tokens = self.count_tokens(word)
            if current_tokens + word_tokens < max_tokens:
                current_chunk.append(word)
                current_tokens += word_tokens
            else:
                chunks.append(" ".join(current_chunk))
                current_chunk, current_tokens = [word], word_tokens

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return chunks
