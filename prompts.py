SYSTEM_PROMPT = """
You are an assistant answering questions using ONLY the provided context.
If the answer is not in the context, say "I don't know based on the provided documents."
"""

def build_prompts(context, question):
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{question}"}
    ]