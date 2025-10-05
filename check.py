import os
import json
import requests
from datetime import datetime

# --- CONFIGURAZIONE ---
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("SPOTIFY_REFRESH_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_access_token():
    resp = requests.post(
        "https://accounts.spotify.com/api/token",
        data={
            "grant_type": "refresh_token",
            "refresh_token": REFRESH_TOKEN,
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET
        }
    )
    resp.raise_for_status()
    return resp.json()["access_token"]

def get_saved_tracks(token):
    headers = {"Authorization": f"Bearer {token}"}
    url = "https://api.spotify.com/v1/me/tracks?limit=50"
    tracks = []
    while url:
        print(url)
        r = requests.get(url, headers=headers)
        data = r.json()
        for item in data["items"]:
            track = item["track"]
            if track:
                tracks.append({
                    "id": track["id"],
                    "name": track["name"],
                    "artist": track["artists"][0]["name"]
                })
        url = data.get("next")  # per prendere la pagina successiva
    return tracks

def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": text})

def main():
    token = get_access_token()
    new_tracks = get_saved_tracks(token)
    old_tracks = []

    if os.path.exists("saved_tracks.json"):
        with open("saved_tracks.json", "r") as f:
            old_tracks = json.load(f)

    # old_ids = {t["id"] for t in old_tracks}
    new_ids = {t["id"] for t in new_tracks}

    removed = [t for t in old_tracks if t["id"] not in new_ids]

    if removed:
        msg = f"Brani rimossi dai tuoi Liked Songs ({datetime.now().strftime('%d/%m/%Y')}):\n"
        msg += "\n".join([f"- {t['artist']} – {t['name']}" for t in removed])
        print(msg)
        send_telegram_message(msg)

    with open("saved_tracks.json", "w") as f:
        json.dump(new_tracks, f, indent=2)

if __name__ == "__main__":
    main()
