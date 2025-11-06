from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = GoogleGenerativeAI(model="gemini-2.5-pro")
response = llm.invoke("Sing a ballad of LangChain.")

print(response )
