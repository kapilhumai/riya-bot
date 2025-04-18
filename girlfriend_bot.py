#!/usr/bin/env python3
import json
import time
import random
import sys
from pathlib import Path

# Try import OpenAI (you must `pip install openai` if you want online mode)
try:
    import openai
except ImportError:
    openai = None

# --- Constants ---
EMOJIS = ['😘','😊','😍','😜','💖','🔥','😉','❤️','😇','😈']

# --- Load config ---
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

bot_name  = config.get("bot_name",  "Riya")
user_name = config.get("user_name", "You")
mode      = config.get("mode",      "SFW")      # "SFW" or "NSFW"
online    = config.get("online",    False)      # True = use ChatGPT
api_key   = config.get("api_key",   "")

if online and openai:
    openai.api_key = api_key

# --- Memory setup ---
memory_path = Path("memory.json")
if memory_path.exists():
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
else:
    memory = {"chats": []}

def save_memory():
    memory_path.write_text(json.dumps(memory, indent=2), encoding="utf-8")

# --- Offline reply ---
def get_offline_reply(_):
    path = Path("responses") / f"{mode.lower()}.txt"
    if not path.exists():
        return "Hmm... kuch kehna tha mujhe, par bhool gayi!"
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return random.choice(lines)

# --- Online reply via ChatGPT ---
def get_online_reply(user_text):
    if not openai or not api_key.startswith("sk-"):
        return get_offline_reply(user_text)
    try:
        messages = [
            {"role": "system",
             "content": (
                 f"You are {bot_name}, a sweet & naughty Indian girlfriend who speaks in Hinglish. "
                 f"Keep replies short, flirty, and true to the {mode} mode."
             )},
            {"role": "user", "content": user_text}
        ]
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.8,
            max_tokens=200
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Oops, kuch error hua: {e}"

# --- Main chat loop ---
def main():
    global bot_name, user_name, mode, online

    print(f"{bot_name}: Hi {user_name}! I'm here. Type '/help' for commands. {random.choice(EMOJIS)}")

    try:
        while True:
            user_text = input(f"{user_name}: ").strip()
            if not user_text:
                continue

            # Exit
            if user_text.lower() in ('/exit','/quit','exit','quit'):
                reply = f"Bye {user_name}, chat soon!"
                print(f"{bot_name}: {reply} {random.choice(EMOJIS)}")
                break

            # Help
            elif user_text.lower().startswith('/help'):
                reply = (
                    "Commands:\n"
                    "/change_name <name>  – Rename me\n"
                    "/toggle_nsfw         – Switch SFW/NSFW\n"
                    "/exit                – Quit chat"
                )

            # Rename bot
            elif user_text.lower().startswith('/change_name'):
                parts = user_text.split(maxsplit=1)
                if len(parts) == 2 and parts[1].strip():
                    bot_name = parts[1].strip()
                    reply = f"Thik hai, ab se mera naam {bot_name} hai!"
                else:
                    reply = "Kya naam rakhoge mera?"

            # Toggle SFW/NSFW
            elif user_text.lower().startswith('/toggle_nsfw'):
                mode = 'NSFW' if mode == 'SFW' else 'SFW'
                reply = f"Ab mai {mode} mood mein hoon..."
            
            # Regular conversation
            else:
                if online and api_key.startswith("sk-"):
                    reply = get_online_reply(user_text)
                else:
                    reply = get_offline_reply(user_text)

            # Print with emoji
            print(f"{bot_name}: {reply} {random.choice(EMOJIS)}")

            # Save chat to memory
            memory['chats'].append({
                'user': user_text,
                'bot':   reply,
                'mode':  mode,
                'time':  time.time()
            })
            save_memory()

    except (KeyboardInterrupt, EOFError):
        print(f"\n{bot_name}: Bye {user_name}! {random.choice(EMOJIS)}\n")
        save_memory()
        sys.exit(0)


if __name__ == "__main__":
    main()
