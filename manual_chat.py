from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import os
load_dotenv()
from langchain_community.document_loaders import TelegramChatApiLoader

api_hash = os.getenv("TELEGRAM_API_KEY")
api_id = os.getenv("TELEGRAM_CHAT_ID")     
phn = os.getenv("PHN")

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

from telethon import TelegramClient , events, sync

# Telegram API credentials (you must use your real app API ID and API Hash here)
# api_id = int(os.getenv("TELEGRAM_CHAT_ID"))   # Make sure this is an integer
# api_hash = os.getenv("TELEGRAM_API_KEY")
client = TelegramClient("Swagger_07", api_id, api_hash)


async def main():
    await client.start(phn)

    # Send the Gemini-generated response to the chat
    await client.send_message("https://t.me/telenut_bot", response.strip())

    print("Sent response back to Telegram!")

# Run the client
with client:
    client.loop.run_until_complete(main())

#     chat_entity="https://t.me/telenut_bot",  # or the username like 'mychannel'
#     api_hash=api_hash,
#     api_id=api_id,
#     username="Swagger_07"  # optional, used for session caching
# )

# documents = loader.load()

# for doc in documents:
#     print(doc.page_content)
