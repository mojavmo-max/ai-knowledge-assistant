from dotenv import load_dotenv
from openai import OpenAI
import json

load_dotenv()
client = OpenAI()


def call_llm(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extact invoice fields. Return json ONLY. No additonal text. Return no content if invoice is not read-able."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format = {"type": "json_object"}
    )
    
    content = response.choices[0].message.content

    try:
        data = json.loads(content)
        if not content or not data:
            raise ValueError("Empty LLM Response")
    except Exception as e:
        return{
            "error": "LLM_OUTPUT_INVALID",
            "raw_data": content
        }

    required = ["invoice_number", "total", "date"]
    for field in required:
        if "invoice" in data and field not in data["invoice"]:
            data["invoice"][field] = None

    return data
