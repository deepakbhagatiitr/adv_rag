import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Make sure the model name has the 'models/' prefix
model = genai.GenerativeModel(model_name='models/gemini-2.0-flash')

response = model.generate_content("Explain RAG architecture in simple terms.")
print(response.text)
