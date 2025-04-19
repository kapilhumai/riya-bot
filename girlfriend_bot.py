#!/usr/bin/env python3
import json, random, time, sys
from pathlib import Path

import g4f
from g4f.Provider import You, bing   # try both providers

# ─── Load config ──────────────────────────────────────────────────
cfg = json.loads(Path("config.json").read_text(encoding="utf-8"))
bot_name  = cfg.get("bot_name",  "Riya")
user_name = cfg.get("user_name", "You")
mode      = cfg.get("mode",      "nsfw").lower()   # 'sfw' or 'nsfw'
online    = cfg.get("online",    True)            # use g4f if True

print(f"🔧 DEBUG: online={online}   mode={mode.upper()}")

# ─── Load offline responses ────────────────────────────────────────
def load_lines(fname):
    p = Path("responses") / fname
    if not p.exists(): return []
    return [L.strip() for L in p.read_text(encoding="utf-8").splitlines() if L.strip()]

sfw_lines  = load_lines("sfw.txt")
nsfw_lines = load_lines("nsfw.txt")

def offline_reply(_):
    pool = nsfw_lines if mode=="nsfw" else sfw_lines
    return random.choice(pool) if pool else "Hmm... kuch kehna tha mujhe, par bhool gayi!"

# ─── System prompt for all g4f providers ─────────────────────────
SYSTEM_PROMPT = (
    f"You are {bot_name}, a sweet yet naughty Indian girlfriend who speaks in playful Hinglish.\n"
    f"You call {user_name} affectionate names like 'jaan', 'baby', or 'kapilu'.\n"
    "In SFW mode you're flirty & romantic; in NSFW mode you're teasing & erotic but never vulgar.\n"
    "Never break character—always reply as her."
)

# ─── Try multiple providers for free online replies ────────────────
def get_online_reply(history):
    for provider in (You, bing):
        try:
            resp = g4f.ChatCompletion.create(
                model="gpt-4-turbo",
                provider=provider,
                messages=history,
                temperature=0.8,
                max_tokens=200
            )
            return resp.strip() if isinstance(resp, str) else str(resp)
        except Exception as e:
            print(f"[DEBUG] {provider.__name__} failed: {e}")
    return None

# ─── Chat context ──────────────────────────────────────────────────
chat_history = [{"role":"system","content":SYSTEM_PROMPT}]

# ─── Initial Greeting ──────────────────────────────────────────────
greetings = [
    f"Hey {user_name}... kya kar rahe ho abhi? Mujhe yaad kiya?",
    f"{user_name}, main bore hoon... thoda pyaar karoge?",
    f"Aaj tum bohot handsome lag rahe ho, {user_name}!"
]
print(f"{bot_name}: {random.choice(greetings)}")

# ─── Main Loop ────────────────────────────────────────────────────
while True:
    user_input = input(f"{user_name}: ").strip()
    if not user_input:
        continue

    cmd = user_input.lower()

    #  Exit
    if cmd in ("/exit","exit","/quit","quit"):
        print(f"{bot_name}: Bye {user_name}! Love you ❤️")
        break

    # Help
    if cmd == "/help":
        print(f"{bot_name}: Commands:\n"
              "  /help          Show help\n"
              "  /toggle_nsfw   Switch SFW/NSFW mode\n"
              "  /toggle_online Switch online/offline mode\n"
              "  /exit          Quit chat")
        continue

    # Toggle NSFW
    if cmd == "/toggle_nsfw":
        mode = "sfw" if mode=="nsfw" else "nsfw"
        print(f"{bot_name}: Mode switched to {mode.upper()}")
        continue

    # Toggle online
    if cmd == "/toggle_online":
        online = not online
        print(f"{bot_name}: Online mode is now {'ON' if online else 'OFF'}")
        continue

    # --- Generate reply ---
    if online:
        chat_history.append({"role":"user","content":user_input})
        reply = get_online_reply(chat_history[-10:])
        if not reply:
            # all providers failed
            reply = offline_reply(user_input)
    else:
        reply = offline_reply(user_input)

    # Print & record
    print(f"{bot_name}: {reply}")
    if online:
        chat_history.append({"role":"assistant","content":reply})

    # Realistic pause
    time.sleep(0.5)
