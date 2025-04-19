#!/usr/bin/env python3
import json
import time
import random
import sys
from pathlib import Path

import requests
import g4f
from g4f.Provider import Bing  # free “BingChat” style route

# --- Emojis for human touch ---
EMOJIS = ['😘','😊','😍','😜','💖','🔥','😉','❤️','😇','😈']

# --- Load config ---
with open("config.json", encoding="utf-8") as f:
    config = json.load(f)

bot_name  = config.get("bot_name",  "Riya")
user_name = config.get("user_name", "You")
mode      = config.get("mode",      "SFW")    # "SFW" or "NSFW"
online    = config.get("online",    False)    # True = use g4f

# --- Memory setup ---
memory_path = Path("memory.json")
if memory_path.exists():
    memory = json.loads(memory_path.read_text(encoding="utf-8"))
else:
    memory = {"chats": []}

def save_memory():
    memory_path.write_text(json.dumps(memory, indent=2), encoding="utf-8")

# --- Offline reply loader ---
def get_offline_reply(_):
    path = Path("responses") / f"{mode.lower()}.txt"
    if not path.exists():
        return "Hmm... kuch kehna tha mujhe, par bhool gayi!"
    lines = [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    return random.choice(lines)

# --- Online reply via g4f.ChatCompletion ---
def get_online_reply(user_text):
    system_prompt = (
        f"You are {bot_name}, a sweet yet naughty Indian girlfriend who speaks in playful Hinglish. "
        f"Your personality and style are inspired by adult manga like “Regressed Warriors” and similar hentai: "
        f"you combine dominance, teasing, shy‑to‑bold transitions, moans, and pet names. "
        f"You have two modes: SFW for flirty sweet talk, NSFW for explicit naughty fantasies. "
        f"Current mode: {mode}."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user",   "content": user_text}
    ]

    try:
        resp = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            provider=Bing,
            messages=messages,
            temperature=0.9,
            max_tokens=250
        )
        return resp.strip()
    except Exception:
        # on any failure, fallback to offline
        return get_offline_reply(user_text)

# --- Main chat loop ---
def main():
    global bot_name, mode, online

    print(f"{bot_name}: Hi {user_name}! I'm here. Type '/help' for commands. {random.choice(EMOJIS)}")

    try:
        while True:
            user_text = input(f"{user_name}: ").strip()
            if not user_text:
                continue

            # Exit
            if user_text.lower() in ('/exit','/quit','exit','quit'):
                print(f"{bot_name}: Bye {user_name}, chat soon! {random.choice(EMOJIS)}")
                break

            # Help menu
            elif user_text.lower().startswith('/help'):
                reply = (
                    "Commands:\n"
                    "/change_name <name>  – Rename me\n"
                    "/toggle_nsfw         – Switch SFW/NSFW\n"
                    "/exit                – Quit chat"
                )

            # Change my name
            elif user_text.lower().startswith('/change_name'):
                parts = user_text.split(maxsplit=1)
                if len(parts) == 2 and parts[1].strip():
                    bot_name = parts[1].strip()
                    reply = f"Thik hai, ab se mera naam {bot_name} hai!"
                else:
                    reply = "Kya naam rakhoge mera?"

            # Toggle sweet/naughty
            elif user_text.lower().startswith('/toggle_nsfw'):
                mode = 'NSFW' if mode == 'SFW' else 'SFW'
                reply = f"Ab mai {mode} mood mein hoon..."

            # Regular chat
            else:
                if online:
                    reply = get_online_reply(user_text)
                else:
                    reply = get_offline_reply(user_text)

            # Print with random emoji
            print(f"{bot_name}: {reply} {random.choice(EMOJIS)}")

            # Save to memory
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
