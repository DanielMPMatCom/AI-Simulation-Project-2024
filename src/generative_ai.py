import google.generativeai as genai
from dotenv import dotenv_values

secrets = dotenv_values(".env")

GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]


class GenAIModel:
    def __init__(self, system_instruction=None) -> None:
        genai.configure(api_key=GOOGLE_API_KEY)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash", system_instruction=system_instruction
        )

    def ask_model(self, question: str) -> str:
        return self.model.generate_content(question).text


## use example
# from generative_ai import GenAIModel
# model = GenAIModel()
# ans = model.ask_model("What is the meaning of life?")
# print(ans)
