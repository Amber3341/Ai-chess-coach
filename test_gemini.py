import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("No GEMINI_API_KEY found in environment.")
else:
    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents="Hello, this is a test.",
        )
        print("Success! Response:")
        print(response.text)
    except Exception as e:
        print(f"Error calling Gemini: {e}")
