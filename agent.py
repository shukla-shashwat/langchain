from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
response = llm.invoke("Sing a ballad of LangChain.")

print(response.content)
