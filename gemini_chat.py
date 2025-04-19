import requests

API_KEY = "AIzaSyDy7i8_pDjo3wqjPCRRNaNFLA6Xo-raln4"
MODEL = "models/gemini-pro"

def ask_gemini(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/{MODEL}:generateContent?key={API_KEY}"
    headers = { "Content-Type": "application/json" }
    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("[Gemini ERROR]", e)
        return "Mujhe abhi kuch samajh nahi aaya..."

while True:
    user = input("You: ")
    if user.lower() in ["exit", "quit"]:
        print("Riya: Bye jaan, fir milte hain!")
        break
    reply = ask_gemini(user)
    print("Riya:", reply)
