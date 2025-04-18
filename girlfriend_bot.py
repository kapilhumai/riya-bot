#!/usr/bin/env python3
import os
import json
import random
import time
import sys

# Try importing OpenAI for online mode
try:
    import openai
except ImportError:
    openai = None

# --- File paths ---
dir_path = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(dir_path, 'config.json')
MEMORY_PATH = os.path.join(dir_path, 'memory.json')
SFW_PATH = os.path.join(dir_path, 'responses', 'sfw.txt')
NSFW_PATH = os.path.join(dir_path, 'responses', 'nsfw.txt')

# --- Load Config ---
with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
    config = json.load(f)
bot_name = config.get('bot_name', 'Riya')
user_name = config.get('user_name', 'User')
mode = config.get('mode', 'sfw')       # 'sfw' or 'nsfw'
online = config.get('online', False)   # True to use OpenAI
api_key = config.get('api_key', '')

# Setup OpenAI if needed
if online and openai:
    openai.api_key = api_key

# --- Load responses from files ---
def load_lines(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

sfw_lines = load_lines(SFW_PATH)
nsfw_lines = load_lines(NSFW_PATH)

# --- Load or init memory ---
if os.path.exists(MEMORY_PATH):
    with open(MEMORY_PATH, 'r', encoding='utf-8') as f:
        memory = json.load(f)
else:
    memory = {'chats': []}

# --- Helpers ---

def save_config():
    config.update({
        'bot_name': bot_name,
        'user_name': user_name,
        'mode': mode,
        'online': online,
        'api_key': api_key
    })
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)


def save_memory():
    with open(MEMORY_PATH, 'w', encoding='utf-8') as f:
        json.dump(memory, f, indent=2)


def get_offline_reply(user_text):
    lines = sfw_lines if mode == 'sfw' else nsfw_lines
    if not lines:
        return "(Sorry, koi reply available nahi hai abhi.)"
    return random.choice(lines)


def get_online_reply(user_text):
    if not openai or not online:
        return get_offline_reply(user_text)
    # Build system prompt
    system_msg = f"You are a desi girlfriend named {bot_name}. You speak in casual Hinglish and sometimes emotional. " \
                 f"You have two modes: SFW for sweet flirty talk, NSFW for naughty explicit talk. " \
                 f"Current mode: {mode.upper()}. Respond accordingly."
    messages = [
        {'role': 'system', 'content': system_msg},
        {'role': 'user', 'content': user_text}
    ]
    try:
        resp = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=messages,
            temperature=0.9,
            max_tokens=250
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return get_offline_reply(user_text)

# --- Main Loop ---

def main():
    global bot_name, mode
    print(f"{bot_name}: Hi {user_name}! I'm here. Type '/help' for commands.")
    try:
        while True:
            user_text = input(f"{user_name}: ").strip()
            if not user_text:
                continue

            # Commands
            if user_text.lower().startswith('/change_name'):
                parts = user_text.split(maxsplit=1)
                if len(parts) == 2:
                    new_name = parts[1].strip()
                    bot_name = new_name
                    save_config()
                    reply = f"Theek hai {user_name}, ab se mera naam {bot_name} hoga."
                else:
                    reply = f"Usage: /change_name <new_name>"

            elif user_text.lower().startswith('/toggle_nsfw') or user_text.lower().startswith('/togglemode'):
                mode = 'nsfw' if mode == 'sfw' else 'sfw'
                save_config()
                tag = 'Naughty' if mode == 'nsfw' else 'Sweet'
                reply = f"Mode switched to {mode.upper()} ({tag})"

            elif user_text.lower() in ['/exit', '/quit', 'exit', 'quit']:
                reply = f"Bye {user_name}, chat soon! 😘"
                print(f"{bot_name}: {reply}")
                break

            elif user_text.lower().startswith('/help'):
                reply = ("Commands:\n" 
                         "/change_name <name> - Rename me.\n" 
                         "/toggle_nsfw - Switch SFW/NSFW mode.\n" 
                         "/exit - Quit chat.")

            else:
                # Regular conversation
                if online:
                    reply = get_online_reply(user_text)
                else:
                    reply = get_offline_reply(user_text)

            # Print and record
            print(f"{bot_name}: {reply}")
            memory['chats'].append({'user': user_text, 'bot': reply, 'mode': mode, 'time': time.time()})
            save_memory()

    except (KeyboardInterrupt, EOFError):
        print(f"\n{bot_name}: Bye {user_name}!\n")
        save_memory()
        sys.exit(0)

if __name__ == '__main__':
    main()
