from transformers import pipeline

generator = pipeline("text-generation", model="sberbank-ai/rugpt3small_based_on_gpt2")

def ai_response(user_text: str):
    result = generator(user_text, max_length=100, num_return_sequences=1)
    return result[0]["generated_text"]