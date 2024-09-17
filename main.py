from generative_ai import GenAIModel

model = GenAIModel()

ans = model.ask_model("What is the meaning of life?")

print(ans)