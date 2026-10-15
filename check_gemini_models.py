
import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai

load_dotenv(Path(__file__).parent / ".env")

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing from .env")

client = genai.Client(api_key=api_key)

models = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
]

for model in models:
    print(f"\nTesting {model}...")
    start = time.perf_counter()

    try:
        response = client.models.generate_content(
            model=model,
            contents=(
                'Return valid JSON only: '
                '{"name":"Test User","skills":["Python","SQL"]}'
            ),
        )

        elapsed = time.perf_counter() - start

        print("Status: SUCCESS")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Response: {response.text}")

    except Exception as error:
        elapsed = time.perf_counter() - start
        print("Status: FAILED")
        print(f"Time: {elapsed:.2f} seconds")
        print(f"Error: {error}")
