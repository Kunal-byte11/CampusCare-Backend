import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
with open('models2.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(models))
