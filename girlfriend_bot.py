#!/usr/bin/env python3
import json
import random
import time
from pathlib import Path

import g4f
from g4f.Provider import You

# ─── Load config ──────────────────────────────────────────────────
with open("config.json", "r", encoding="utf-8") as f:
    cfg = json.load(f)

bot_name  = cfg.get("bot_name",  "Riya")
user_name = cfg.get("user_name", "You")
mode      = cfg.get("mode",      "nsfw").lower()   # 'sfw' or 'nsfw'
online    = cfg.get("online",    True)            # use g4f if True

print(f"🔧 DEBUG: online={online}   mode={mode.upper()}")

# ─── Load offline responses ────────────────────────────────────────
def load_lines(fname):
    p = Path("responses") / fname
    if not p.exists():
        return []
    return [L.strip() for L in p.read_text(encoding="utf-8").splitlines() if L.strip()]

sfw_lines  = load_lines("sfw.txt")
nsfw_lines = load_lines("nsfw.txt")

def offline_reply(_):
    pool = nsfw_lines if mode == "nsfw" else sfw_lines
    return random.choice(pool) if pool else "Hmm... kuch kehna tha mujhe, par bhool gayi!"

# ─── Personality system prompt ────────────────────────────────────
SYSTEM_PROMPT = (
    f"You are {bot_name}, a sweet yet naughty Indian girlfriend who speaks in playful Hinglish. "
    f"You call {user_name} affectionate names like 'jaan', 'baby', or 'kapilu'. "
    "In SFW mode you're flirty and romantic; in NSFW mode you can be teasing and erotic but never vulgar. "
    "Never break character—always reply as her."
)

# ─── Chat context ──────────────────────────────────────────────────
chat_history = [{"role": "system", "content": SYSTEM_PROMPT}]

# ─── Initial Greeting ──────────────────────────────────────────────
greetings = [
    f"Hey {user_name}... kya kar rahe ho abhi? Mujhe yaad kiya?",
    f"{user_name}, main thodi bored hoon... thoda pyaar karoge?",
    f"Aaj tum bohot handsome lag rahe ho, {user_name}!"
]
print(f"{bot_name}: {random.choice(greetings)}")

# ─── Main Loop ────────────────────────────────────────────────────
while True:
    user_input = input(f"{user_name}: ").strip()
    if not user_input:
        continue

    cmd = user_input.lower()

    # Exit
    if cmd in ("/exit","exit","/quit","quit"):
        print(f"{bot_name}: Bye {user_name}! Love you ❤️")
        break

    # Help
    if cmd == "/help":
        print(f"{bot_name}: Commands:\n"
              "  /help          Show this help\n"
              "  /toggle_nsfw   Switch SFW/NSFW mode\n"
              "  /toggle_online Switch online/offline mode\n"
              "  /exit          Quit chat")
        continue

    # Toggle SFW/NSFW
    if cmd == "/toggle_nsfw":
        mode = "sfw" if mode == "nsfw" else "nsfw"
        print(f"{bot_name}: Mode switched to {mode.upper()}")
        continue

    # Toggle online/offline
    if cmd == "/toggle_online":
        online = not online
        print(f"{bot_name}: Online mode is now {'ON' if online else 'OFF'}")
        continue

    # Generate reply
    if online:
        chat_history.append({"role": "user", "content": user_input})
        try:
            resp = g4f.ChatCompletion.create(
                model="gpt-4-turbo",
                provider=You,
                messages=chat_history[-10:],  # keep last 10 msgs
                temperature=0.8,
                max_tokens=200
            )
            reply = resp.strip() if isinstance(resp, str) else str(resp)
        except Exception:
            reply = offline_reply(user_input)
    else:
        reply = offline_reply(user_input)

    # Print and record
    print(f"{bot_name}: {reply}")
    if online:
        chat_history.append({"role": "assistant", "content": reply})

    # small pause for realism
    time.sleep(0.5)
