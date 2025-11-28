import json
import os
from telethon import TelegramClient, events

# Railway se environment variables
api_id = int(os.environ["API_ID"])
api_hash = os.environ["API_HASH"]

# Mapping file
MAPPING_FILE = "mapping.json"

# Agar mapping.json nahi mile to create karo
if not os.path.exists(MAPPING_FILE):
    with open(MAPPING_FILE, "w") as f:
        json.dump({"sources": [], "targets": []}, f)

def load_mapping():
    with open(MAPPING_FILE, "r") as f:
        return json.load(f)

def save_mapping(data):
    with open(MAPPING_FILE, "w") as f:
        json.dump(data, f, indent=4)

# User account session use hoga
client = TelegramClient("mysession", api_id, api_hash)


# -------------------- COMMANDS ------------------------

# Add Source
@client.on(events.NewMessage(pattern=r"add source (.+)"))
async def add_source(event):
    chat = event.pattern_match.group(1)
    entity = await client.get_entity(chat)
    chat_id = entity.id

    data = load_mapping()
    if chat_id not in data["sources"]:
        data["sources"].append(chat_id)
        save_mapping(data)
        await event.reply(f"✔ Source added: {chat} ({chat_id})")
    else:
        await event.reply("⚠ यह source पहले से मौजूद है.")

# Add Target
@client.on(events.NewMessage(pattern=r"add target (.+)"))
async def add_target(event):
    chat = event.pattern_match.group(1)
    entity = await client.get_entity(chat)
    chat_id = entity.id

    data = load_mapping()
    if chat_id not in data["targets"]:
        data["targets"].append(chat_id)
        save_mapping(data)
        await event.reply(f"✔ Target added: {chat} ({chat_id})")
    else:
        await event.reply("⚠ यह target पहले से मौजूद है.")

# List all
@client.on(events.NewMessage(pattern=r"list"))
async def list_all(event):
    data = load_mapping()
    msg = "📌 Sources:\n" + "\n".join([str(s) for s in data["sources"]])
    msg += "\n\n📌 Targets:\n" + "\n".join([str(t) for t in data["targets"]])
    await event.reply(msg)

# Remove Source
@client.on(events.NewMessage(pattern=r"remove source (.+)"))
async def remove_source(event):
    cid = int(event.pattern_match.group(1))
    data = load_mapping()

    if cid in data["sources"]:
        data["sources"].remove(cid)
        save_mapping(data)
        await event.reply("✔ Source removed.")
    else:
        await event.reply("❌ Source not found.")

# Remove Target
@client.on(events.NewMessage(pattern=r"remove target (.+)"))
async def remove_target(event):
    cid = int(event.pattern_match.group(1))
    data = load_mapping()

    if cid in data["targets"]:
        data["targets"].remove(cid)
        save_mapping(data)
        await event.reply("✔ Target removed.")
    else:
        await event.reply("❌ Target not found.")


# -------------------- AUTO FORWARD ------------------------

@client.on(events.NewMessage())
async def auto_forward(event):
    data = load_mapping()

    if event.chat_id in data["sources"]:
        for target in data["targets"]:
            try:
                await client.forward_messages(target, event.message)
            except Exception as e:
                print("Error:", e)


print("🚀 Bot Started Successfully!")
client.start()
client.run_until_disconnected()
