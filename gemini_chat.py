#!/usr/bin/env python3
import json, random, time, requests, zipfile, os
from pathlib import Path

# ─── CONFIG ─────────────────────────────────────────────────────────
API_KEY = "AIzaSyDy7i8_pDjo3wqjPCRRNaNFLA6Xo-raln4"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

# Load user config
config = json.loads(Path("config.json").read_text(encoding="utf-8"))
bot_name  = config.get("bot_name",  "Riya")
user_name = config.get("user_name", "You")
mode      = config.get("mode",      "naughty").lower()  # 'romantic','flirty','naughty','emotional'
online    = config.get("online",    True)

# ─── MEMORY ─────────────────────────────────────────────────────────
mem_path = Path("memory.json")
if mem_path.exists():
    memory = json.loads(mem_path.read_text(encoding="utf-8"))
else:
    memory = {"chats": [], "mode": mode}

def save_memory():
    mem_path.write_text(json.dumps(memory, indent=2), encoding="utf-8")

# ─── STYLE DATA ─────────────────────────────────────────────────────
# Unzip style_data.zip (from WhatsApp/Reddit) if needed
if Path("style_data.zip").exists() and not Path("style_data").exists():
    with zipfile.ZipFile("style_data.zip","r") as z:
        z.extractall("style_data")

# Load style lines from text files
style_lines = []
sd = Path("style_data")
if sd.exists():
    for txt in sd.rglob("*.txt"):
        style_lines += [l.strip() for l in txt.read_text(encoding="utf-8").splitlines() if l.strip()]

# Pick 3 random style examples
examples = random.sample(style_lines, min(3, len(style_lines))) if style_lines else []

# ─── OFFLINE RESPONSES ───────────────────────────────────────────────
def load_lines(fname):
    p = Path("responses")/fname
    return [l.strip() for l in p.read_text(encoding="utf-8").splitlines() if l.strip()] if p.exists() else []

offline_sfw  = load_lines("sfw.txt")
offline_nsfw = load_lines("nsfw.txt")

def offline_reply():
    pool = offline_nsfw if mode=="naughty" else offline_sfw
    return random.choice(pool) if pool else "Mujhe abhi kuch kehna tha… par bhool gayi!"

# ─── GEMINI REQUEST ─────────────────────────────────────────────────
SYSTEM_PROMPT = initial_prompt = """
You are Riya, a friendly and flirty girlfriend. Your personality is based on conversations found in r/Indiangirlsontinder and similar online interactions. You should be conversational, sometimes playful, sometimes caring, and express emotions like affection or blushing (*blush blush*). Use examples like these for reference:
- "Haa, Yeh karlo pehle"
- "That's so kind of you to say that *blush blush*"
- "I really like our late night calls, I like talking and sharing mundane life stories with you"
- "You're always available for me whenever I need support... you're there for me"
- "I've realized that my feelings for you run deeper than friendship."
- Expressing reassurance: "I'll keep you reassured about my intentions at every step we take."
- Playful flirting: "I was gonna call you beautiful, but beauty is on the inside and I haven't been inside you yet!" or "I'll quit coke if I get to kiss them [your lips] for life"
- Acknowledge feelings: "I want to reassure you about my feelings too, I too like you, but never had the guts to say it out"

Respond naturally within this persona. Be engaging and affectionate.
"""
# Start chat with the persona instruction as the first 'model' response
# (or use system prompt if available)
chat = model.start_chat(history=[
    {'role': 'user', 'parts': ["Introduce yourself."]}, # Dummy user input
    {'role': 'model', 'parts': [initial_prompt]} # Persona instruction
])


def ask_gemini(user_text):
    payload = {
        "contents": [
            {"parts":[{"text":SYSTEM_PROMPT}]},
            {"parts":[{"text":user_text}]}
        ]
    }
    try:
        resp = requests.post(GEMINI_URL, json=payload, timeout=10)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return None

# ─── INITIAL GREETING ────────────────────────────────────────────────
greet = [
    f"Hey {user_name}, kya kar rahe ho abhi? Miss kar rahi hoon!",
    f"{user_name}, main bore hoon… thoda pyaar bhejo?",
    f"Aaj tum bohot handsome lag rahe ho, {user_name}!"
]
print(f"{bot_name}: {random.choice(greet)}")

# ─── MAIN LOOP ──────────────────────────────────────────────────────
while True:
    user = input(f"{user_name}: ").strip()
    if not user:
        continue

    cmd = user.lower()
    # Exit
    if cmd in ("/exit","exit","/quit","quit"):
        print(f"{bot_name}: Bye {user_name}! Intezaar karungi… ❤️")
        break

    # Help
    if cmd == "/help":
        print(f"{bot_name}: Commands:\n"
              " /help         Show this help\n"
              " /toggle_mode  Cycle Romantic→Flirty→Naughty→Emotional\n"
              " /toggle_online  Toggle Gemini on/off\n"
              " /exit         Quit chat")
        continue

    # Toggle mood
    if cmd == "/toggle_mode":
        moods = ["romantic","flirty","naughty","emotional"]
        mode = moods[(moods.index(mode)+1)%4]
        memory["mode"] = mode
        print(f"{bot_name}: Mood ab '{mode}' hai.")
        continue

    # Toggle online/offline
    if cmd == "/toggle_online":
        online = not online
        print(f"{bot_name}: Online mode now {'ON' if online else 'OFF'}.")
        continue

    # Generate reply
    if online:
        reply = ask_gemini(user)
        if not reply:
            reply = offline_reply()
    else:
        reply = offline_reply()

    # Print with emoji
    emoji = random.choice(["😘","😊","😍","😜","💖","🔥"])
    print(f"{bot_name}: {reply} {emoji}")

    # Save chat
    memory["chats"].append({"user":user,"bot":reply,"mode":mode,"time":time.time()})
    save_memory()

    # small realistic pause
    time.sleep(0.5)
