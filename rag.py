from retrieve import retrieve
from openai import OpenAI
from dotenv import load_dotenv
from prompts import build_prompts
import logging

logging.basicConfig(level=logging.INFO)
logging.info("Retrieving context")

load_dotenv()
client = OpenAI()

def answer(question):
    chunks = retrieve(question)
    context = "\n\n".join(chunks)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=build_prompts(context, question),
        temperature=0
    )

    return response.choices[0].message.content

if __name__ == "__main__":
    questions = [
        "What is this document about?",
        "Summarize the main points.",
        "What is the CEO's phone number?"
    ]

    for q in questions:
        print("\nQ: ", q)
        print("\nA: ", answer(q))