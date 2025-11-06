from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()
from langchain_community.document_loaders import TelegramChatApiLoader

api_hash = os.getenv("TELEGRAM_API_KEY")
api_id = os.getenv("TELEGRAM_CHAT_ID")     

loader = TelegramChatApiLoader(
    chat_entity="https://t.me/telenut_bot",  # or the username like 'mychannel'
    api_hash=api_hash,
    api_id=api_id,
    username="Swagger_07"  # optional, used for session caching
)
documents = loader.load()
print(f"Loaded {len(documents)} documents from Telegram chat.")
# print(documents[0].page_content)

# # Extract the actual messages within the big document
full_content = documents[0].page_content

# Split into individual lines/messages
lines = full_content.strip().split("\n")

# Latest message is the last line
latest_message = lines[0]
print("Latest message:", latest_message)

# prompt = f"give me the result based on my prompt which is: {latest_message}"
# print(prompt)
llm = GoogleGenerativeAI(model="gemini-2.5-pro")
response = llm.invoke(f"give me the result based on my prompt which is: {latest_message}")
print(response)

# from langchain_community.document_loaders import TelegramChatApiLoader

# loader = TelegramChatApiLoader(
#     chat_entity="https://t.me/telenut_bot",  # or the username like 'mychannel'
#     api_hash=api_hash,
#     api_id=api_id,
#     username="Swagger_07"  # optional, used for session caching
# )

# documents = loader.load()

# for doc in documents:
#     print(doc.page_content)
