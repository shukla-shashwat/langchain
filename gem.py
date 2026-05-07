import os, json, re, datetime
from pathlib import Path
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputFile
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from notion_client import Client
from langchain_google_genai import GoogleGenerativeAI

# ============ SETUP ============
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_PARENT_PAGE_ID = os.getenv("NOTION_PARENT_PAGE_ID")
NOTION_TASK_DB_ID = os.getenv("NOTION_TASK_DB_ID", "")  # optional task database

llm = GoogleGenerativeAI(model="gemini-2.5-pro")
notion = Client(auth=NOTION_API_KEY)

FAV_FILE = Path("favorites.json")
if not FAV_FILE.exists():
    FAV_FILE.write_text(json.dumps([]))


# ============ UTILS ============

def get_all_pages():
    """Fetch all child pages under parent."""
    pages = []
    try:
        res = notion.blocks.children.list(NOTION_PARENT_PAGE_ID)
        for b in res.get("results", []):
            if b["type"] == "child_page":
                pages.append({
                    "id": b["id"],
                    "title": b["child_page"]["title"]
                })
    except Exception as e:
        print("Error fetching pages:", e)
    return pages


def get_recent_pages(limit=5):
    pages = []
    try:
        res = notion.search()
        for p in res["results"]:
            if p["object"] == "page":
                pages.append({
                    "id": p["id"],
                    "title": p["properties"]["title"]["title"][0]["plain_text"],
                    "edited": p["last_edited_time"],
                })
        pages.sort(key=lambda x: x["edited"], reverse=True)
        return pages[:limit]
    except Exception:
        return []


def fetch_page_content(page_id):
    """Combine text from Notion page blocks."""
    blocks = notion.blocks.children.list(page_id).get("results", [])
    text = []
    for b in blocks:
        t = b["type"]
        if t in ["paragraph", "heading_1", "heading_2", "heading_3", "quote", "to_do"]:
            rich = b[t].get("rich_text", [])
            for r in rich:
                if r.get("plain_text"):
                    text.append(r["plain_text"])
    return "\n".join(text)


def append_block(page_id, content, block_type="paragraph"):
    block = {"object": "block", "type": block_type,
             block_type: {"rich_text": [{"text": {"content": content}}]}}
    notion.blocks.children.append(page_id, children=[block])
    return "📝 Content appended."


def create_page(title, content, template="blank"):
    blocks = []
    if template == "journal":
        content = f"Journal entry ({datetime.date.today()}):\n" + content
    elif template == "research":
        content = f"Research Notes:\n{content}"
    blocks.append({
        "object": "block", "type": "paragraph",
        "paragraph": {"rich_text": [{"text": {"content": content}}]}
    })
    notion.pages.create(parent={"page_id": NOTION_PARENT_PAGE_ID},
                        properties={"title": [{"text": {"content": title}}]},
                        children=blocks)
    return f"✅ Page '{title}' created."


def search_pages(query):
    res = notion.search(query=query)
    matches = []
    for p in res.get("results", []):
        if p["object"] == "page":
            title = p["properties"]["title"]["title"][0]["plain_text"]
            matches.append({"title": title, "id": p["id"]})
    return matches


def export_page(page_id):
    content = fetch_page_content(page_id)
    filename = f"notion_export_{page_id[:6]}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def toggle_favorite(page_title):
    favs = json.loads(FAV_FILE.read_text())
    if page_title in favs:
        favs.remove(page_title)
        FAV_FILE.write_text(json.dumps(favs))
        return "⭐ Removed from favorites."
    favs.append(page_title)
    FAV_FILE.write_text(json.dumps(favs))
    return "⭐ Added to favorites."


# ============ TELEGRAM HANDLERS ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Welcome! Use /pages to manage Notion pages.")


async def pages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 View Pages", callback_data="list_pages")],
        [InlineKeyboardButton("🕓 Recent Pages", callback_data="recent")],
        [InlineKeyboardButton("⭐ Favorites", callback_data="favorites")],
        [InlineKeyboardButton("🔍 Search", callback_data="search")],
        [InlineKeyboardButton("🆕 Create New Page", callback_data="create_page_menu")],
        [InlineKeyboardButton("✅ Create Task", callback_data="create_task")]
    ]
    await update.message.reply_text("📚 Choose an option:",
                                    reply_markup=InlineKeyboardMarkup(keyboard))


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data

    # list all pages
    if data == "list_pages":
        pages = get_all_pages()
        if not pages:
            await q.message.reply_text("No pages found.")
            return
        keyboard = []
        for p in pages:
            keyboard.append([InlineKeyboardButton(p["title"], callback_data=f"page_{p['id']}")])
        await q.message.reply_text("Select a page:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data == "recent":
        rec = get_recent_pages()
        msg = "\n".join([f"🕓 {p['title']}" for p in rec])
        await q.message.reply_text(msg or "No recent pages found.")
        return

    if data == "favorites":
        favs = json.loads(FAV_FILE.read_text())
        await q.message.reply_text("⭐ Favorites:\n" + "\n".join(favs) if favs else "No favorites yet.")
        return

    if data == "search":
        await q.message.reply_text("🔍 Enter search term:")
        context.user_data["searching"] = True
        return

    if data.startswith("page_"):
        pid = data.replace("page_", "")
        context.user_data["page_id"] = pid
        page = notion.pages.retrieve(pid)
        title = page["properties"]["title"]["title"][0]["plain_text"]
        url = page["url"]
        keyboard = [
            [InlineKeyboardButton("👁️ View (Summarize)", callback_data=f"view_{pid}")],
            [InlineKeyboardButton("✏️ Append", callback_data=f"append_{pid}")],
            [InlineKeyboardButton("⭐ Favorite", callback_data=f"fav_{title}")],
            [InlineKeyboardButton("📤 Export", callback_data=f"export_{pid}")],
            [InlineKeyboardButton("🔗 Open", url=url)],
        ]
        await q.message.reply_text(f"Actions for *{title}*:",
                                   parse_mode="Markdown",
                                   reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("view_"):
        pid = data.replace("view_", "")
        content = fetch_page_content(pid)
        summary = llm.invoke(f"Summarize clearly:\n{content}").strip()
        await q.message.reply_text(f"📖 Summary:\n{summary}")
        return

    if data.startswith("append_"):
        context.user_data["append_id"] = data.replace("append_", "")
        await q.message.reply_text("✏️ Choose block type: paragraph, heading_2, quote, to_do, code")
        context.user_data["await_block_type"] = True
        return

    if data.startswith("export_"):
        pid = data.replace("export_", "")
        file = export_page(pid)
        await q.message.reply_document(InputFile(file))
        os.remove(file)
        return

    if data.startswith("fav_"):
        title = data.replace("fav_", "")
        msg = toggle_favorite(title)
        await q.message.reply_text(msg)
        return

    if data == "create_page_menu":
        keyboard = [
            [InlineKeyboardButton("📝 Blank", callback_data="new_blank")],
            [InlineKeyboardButton("📔 Journal", callback_data="new_journal")],
            [InlineKeyboardButton("🔬 Research", callback_data="new_research")]
        ]
        await q.message.reply_text("Choose template:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("new_"):
        context.user_data["template"] = data.replace("new_", "")
        context.user_data["creating"] = True
        await q.message.reply_text("Enter title for new page:")
        return

    if data == "create_task":
        context.user_data["creating_task"] = True
        await q.message.reply_text("Enter task title:")
        return


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if context.user_data.get("searching"):
        matches = search_pages(text)
        if not matches:
            await update.message.reply_text("No matches found.")
        else:
            msg = "\n".join([f"🔹 {m['title']}" for m in matches])
            await update.message.reply_text(msg)
        context.user_data.clear()
        return

    if context.user_data.get("await_block_type"):
        context.user_data["block_type"] = text.strip()
        context.user_data["await_block_type"] = False
        await update.message.reply_text("Now send content to append:")
        context.user_data["awaiting_append_text"] = True
        return

    if context.user_data.get("awaiting_append_text"):
        pid = context.user_data.pop("append_id")
        btype = context.user_data.pop("block_type", "paragraph")
        msg = append_block(pid, text, btype)
        await update.message.reply_text(msg)
        return

    if context.user_data.get("creating"):
        context.user_data["new_page_title"] = text
        context.user_data["awaiting_content"] = True
        context.user_data["creating"] = False
        await update.message.reply_text("Now send content for the page:")
        return

    if context.user_data.get("awaiting_content"):
        title = context.user_data.pop("new_page_title")
        template = context.user_data.pop("template", "blank")
        reply = create_page(title, text, template)
        await update.message.reply_text(reply)
        return

    if context.user_data.get("creating_task"):
        title = text
        if NOTION_TASK_DB_ID:
            notion.pages.create(
                parent={"database_id": NOTION_TASK_DB_ID},
                properties={"Name": {"title": [{"text": {"content": title}}]}},
            )
            await update.message.reply_text(f"✅ Task '{title}' added to Notion DB.")
        else:
            await update.message.reply_text("⚠️ Task DB ID not configured.")
        context.user_data.clear()
        return

    # Default chat fallback (LLM)
    resp = llm.invoke(f"Respond helpfully to: {text}").strip()
    await update.message.reply_text(resp)


def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("pages", pages))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))
    print("✅ Bot connected to Notion & Gemini.")
    app.run_polling()


if __name__ == "__main__":
    main()
