from telegram.ext import Application, MessageHandler, filters
from langchain_google_genai import GoogleGenerativeAI
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Load credentials
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Initialize Gemini model
llm = GoogleGenerativeAI(model="gemini-2.5-pro")

async def ai_reply(update, context):
    """Handles incoming messages and responds with AI."""
    user_message = update.message.text
    chat_id = update.effective_chat.id
    username = update.effective_user.username or "Unknown User"

    print(f"📩 New message from {username}: {user_message}")

    # Generate response from Gemini
    ai_response = llm.invoke(
        f"Respond helpfully and clearly to the message: {user_message}"
    )

    # Send the AI response back to the chat
    await update.message.reply_text(ai_response.strip())
    print(f"🤖 Bot replied: {ai_response}")

def main():
    # Create application
    app = Application.builder().token(BOT_TOKEN).build()

    # Add handler for all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_reply))

    print("✅ Bot is now listening for messages...")
    app.run_polling()

if __name__ == "__main__":
    main()
