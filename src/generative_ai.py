import google.generativeai as genai
from dotenv import dotenv_values

secrets = dotenv_values(".env")

GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]


class GenAIModel:
    def __init__(self) -> None:
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel("gemini-1.5-flash")

    def ask_model(self, question: str) -> str:
        return self.model.generate_content(question).text
