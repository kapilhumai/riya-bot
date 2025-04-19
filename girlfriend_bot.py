#!/usr/bin/env python3
import json, time, random, sys, threading
from pathlib import Path

import requests
import g4f
from g4f.Provider import Bing

# ── Configuration & State ─────────────────────────────────────────
with open("config.json", encoding="utf-8") as f:
    cfg = json.load(f)

bot_name  = cfg.get("bot_name",  "Riya")
user_name = cfg.get("user_name", "You")
mode      = cfg.get("mode",      "SFW")    # "SFW" or "NSFW"
online    = cfg.get("online",    False)    # True = use g4f

MEM_PATH = Path("memory.json")
if MEM_PATH.exists():
    memory = json.loads(MEM_PATH.read_text(encoding="utf-8"))
else:
    memory = {"chats": []}

def save_memory():
    MEM_PATH.write_text(json.dumps(memory, indent=2), encoding="utf-8")

# ── Load offline responses ────────────────────────────────────────
def load_lines(fn):
    path = Path("responses") / fn
    if not path.exists(): return []
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]

sfw_lines  = load_lines("sfw.txt")
nsfw_lines = load_lines("nsfw.txt")

# ── Auto‑message setup ────────────────────────────────────────────
EMOJIS = ['😘','😊','😍','😜','💖','🔥','😉','❤️','😇','😈']
AUTO_MIN = 45   # seconds
AUTO_MAX = 90

last_user_time = time.monotonic()

def schedule_auto():
    def job():
        global last_user_time
        wait = random.uniform(AUTO_MIN, AUTO_MAX)
        time.sleep(wait)
        # only send if user silent
        if time.monotonic() - last_user_time >= wait:
            line = (nsfw_lines if mode=="NSFW" else sfw_lines) or ["Tumhare bina bohot akela mehsoos ho raha hai..."]
            print(f"\n{bot_name} (auto): {random.choice(line)} {random.choice(EMOJIS)}")
    threading.Thread(target=job, daemon=True).start()

# ── Online via g4f ────────────────────────────────────────────────
SYSTEM_PROMPT = (
    f"You are {bot_name}, a sweet yet daring Indian girlfriend who speaks in playful Hinglish. "
    "Your style is inspired by adult manga: you blend gentle affection with teasing dominance. "
    "Use moans, pet names like 'jaan', 'baby', and describe fantasies vividly in NSFW mode. "
    "In SFW mode be sweet and caring. Never break character."
)

def get_online_reply(text):
    try:
        resp = g4f.ChatCompletion.create(
            model="gpt-3.5-turbo",
            provider=Bing,
            messages=[
                {"role":"system","content":SYSTEM_PROMPT},
                {"role":"user","content":text}
            ],
            temperature=0.9,
            max_tokens=250
        )
        return resp.strip()
    except:
        return None

# ── Offline fallback ──────────────────────────────────────────────
def get_offline_reply(_):
    lines = nsfw_lines if mode=="NSFW" else sfw_lines
    return random.choice(lines) if lines else "Hmm... kuch kehna tha mujhe, par bhool gayi!"

# ── Main Chat Loop ───────────────────────────────────────────────
def main():
    global bot_name, mode, last_user_time

    print(f"{bot_name}: Hi {user_name}! Type '/help' for commands. {random.choice(EMOJIS)}")
    schedule_auto()

    try:
        while True:
            user_text = input(f"{user_name}: ").strip()
            last_user_time = time.monotonic()
            # schedule next auto
            schedule_auto()

            # commands
            cmd = user_text.lower()
            if cmd in ('/exit','exit','/quit','quit'):
                print(f"{bot_name}: Bye {user_name}! {random.choice(EMOJIS)}")
                break

            if cmd.startswith('/help'):
                reply = (
                    "Commands:\n"
                    "/change_name <name>  – Rename me\n"
                    "/toggle_nsfw         – Switch SFW/NSFW\n"
                    "/exit                – Quit chat"
                )

            elif cmd.startswith('/change_name'):
                parts = user_text.split(maxsplit=1)
                if len(parts)==2:
                    bot_name = parts[1].strip()
                    reply = f"Thik hai, ab se mera naam {bot_name} hai!"
                else:
                    reply = "Kya naam rakhoge mera?"

            elif cmd.startswith('/toggle_nsfw'):
                mode = "NSFW" if mode=="SFW" else "SFW"
                reply = f"Ab mai {mode} mood mein hoon..."

            else:
                # normal chat
                if online:
                    reply = get_online_reply(user_text) or get_offline_reply(user_text)
                else:
                    reply = get_offline_reply(user_text)

            print(f"{bot_name}: {reply} {random.choice(EMOJIS)}")

            memory['chats'].append({
                'user': user_text,
                'bot': reply,
                'mode': mode,
                'time': time.time()
            })
            save_memory()

    except (KeyboardInterrupt, EOFError):
        print(f"\n{bot_name}: Bye {user_name}! {random.choice(EMOJIS)}")
        save_memory()
        sys.exit(0)

if __name__=="__main__":
    main()
