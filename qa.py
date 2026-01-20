from retrieve import retrieve
from prompts import build_prompts
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

def question_answer(question: str):
    chunks = retrieve(question)
    context = "\n\n".join(chunks)
    
    if not chunks:
        return "No documents indexed yet."

    try:
        response = client.chat.completions.create(
            model = "gpt-4o-mini",
            messages = build_prompts(context, question),
            temperature = 0
        )
    except Exception as e:
        return "LLM error. Try again later"

    return response.choices[0].message.content