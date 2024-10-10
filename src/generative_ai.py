import google.generativeai as genai
from dotenv import dotenv_values

secrets = dotenv_values(".env")

GOOGLE_API_KEY = secrets["GOOGLE_API_KEY"]


class GenAIModel:
    """
    GenAIModel is a class that interfaces with a generative AI model to generate content based on provided questions.
    Attributes:
        model (genai.GenerativeModel): An instance of the generative AI model.
    Methods:
        __init__(system_instruction=None):
            Initializes the GenAIModel instance and configures the generative AI model.
        ask_model(question: str) -> str:
            Generates content based on the provided question and returns the generated text.
    """

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
