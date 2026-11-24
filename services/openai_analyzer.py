import openai

client = openai.OpenAI()

class OpenAIAnalyzer:
    """Kommuniziert mit OpenAI's API zur Textanalyse."""

    def analyze_text(self, prompt, model="gpt-4o-mini"):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Du bist ein Experte für Textanalyse."},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Fehler bei der OpenAI-Anfrage: {e}")
            return "Fehler in der Analyse"
