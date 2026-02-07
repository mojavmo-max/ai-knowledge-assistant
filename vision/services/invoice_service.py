from dotenv import load_dotenv
from openai import OpenAI
import numpy as np
import json
from vision.services.llm_service import call_llm


def extract_invoice_fields(text):
    prompt = f"""
        Extract invoice data as JSON:
        {text}
    """

    return call_llm(prompt)