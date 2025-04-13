from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import google.generativeai as genai
import os

# Insert your Gemini API key here 👇
GEMINI_API_KEY = "AIzaSyA6q9q7UlGHvqi_133mbURPEeGlz0pJfe0"
genai.configure(api_key=GEMINI_API_KEY)

# Load the Gemini model
model = genai.GenerativeModel("gemini-pro")

app = FastAPI()

@app.post("/ask")
async def ask_ai(request: Request):
    data = await request.json()
    question = data.get("question")
    grade = data.get("grade")
    language = data.get("language")

    # Prepare the prompt for Gemini
    prompt = f"You are an AI tutor helping a Grade {grade} student in {language}. Answer the following in simple {language}:\n\n{question}"

    try:
        # Send question to Gemini
        response = model.generate_content(prompt)
        answer = response.text
    except Exception as e:
        answer = f"⚠️ Error: {str(e)}"

    return JSONResponse(content={"answer": answer})
