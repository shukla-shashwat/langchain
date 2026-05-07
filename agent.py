from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm_model = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash-lite",
    temperature=1,
    max_tokens=299
)

response = llm_model.invoke("What is 2 + 2? Reply with just the number.")
print(response.content)
