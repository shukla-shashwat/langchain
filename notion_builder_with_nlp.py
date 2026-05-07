from notion_client import Client
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables
load_dotenv()


notion = Client(auth=os.getenv("NOTION_API_KEY"))
parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")

page_titles = input("Enter Notion page title: ")

# Create a new standalone page
response = notion.pages.create(
    parent={"page_id": parent_page_id},
    properties={
        "title": [
            {
                "text": {"content": page_titles}

            }
        ]
    },
    children=[
        {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": [{"text": {"content": "This page was created without a database!"}}]
            }
        }
    ]
)



print("✅ Page created!")
page_title = response["properties"]["title"]["title"][0]["plain_text"]
print("📄 Title:", page_title)
page_id = response["id"].replace("-", "")  # UUID without hyphens
print("🆔 Page ID:", page_id)
print("🔗 URL:", response["url"])


def save_page_to_env(page_title, page_id, env_path=".env"):
    env = Path(env_path)

    # Convert title to env key format (uppercase, underscore, no spaces)
    key = page_title.replace(" ", "_").replace("-", "_").upper()
    value = page_id

    # Append to .env file
    with env.open("a") as f:
        f.write(f" \n{key} = {value}\n")

    print(f"🔐 Saved to .env: \n{key}={value}")

save_page_to_env(page_title, page_id, env_path=".env")