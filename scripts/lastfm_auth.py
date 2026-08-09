"""
===========================================================
 MusicCenter
-----------------------------------------------------------
 Last.fm one-time session key helper

 Not part of the Flask app - run this once, by hand, from
 anywhere with Python + internet (doesn't have to be the Pi),
 to turn an API key/secret from last.fm/api into a permanent
 LASTFM_SESSION_KEY for .env. Doesn't touch the running app.

 Usage:
     python scripts/lastfm_auth.py

 Version : 0.1
===========================================================
"""

import hashlib
import webbrowser

import requests

API_URL = "https://ws.audioscrobbler.com/2.0/"


def sign(params, secret):
    ordered = "".join(f"{key}{params[key]}" for key in sorted(params))
    return hashlib.md5((ordered + secret).encode()).hexdigest()


def call(method, params, secret):
    payload = {"method": method, "format": "json", **params}
    payload["api_sig"] = sign({k: v for k, v in payload.items() if k != "format"}, secret)

    response = requests.get(API_URL, params=payload, timeout=10)
    response.raise_for_status()

    data = response.json()

    if "error" in data:
        raise SystemExit(f"Last.fm error {data['error']}: {data.get('message')}")

    return data


def main():
    api_key = input("LASTFM_API_KEY: ").strip()
    api_secret = input("LASTFM_API_SECRET: ").strip()

    token = call("auth.getToken", {"api_key": api_key}, api_secret)["token"]

    auth_url = f"https://www.last.fm/api/auth/?api_key={api_key}&token={token}"
    print(f"\nOткройте эту ссылку, войдите и нажмите Allow:\n{auth_url}\n")

    try:
        webbrowser.open(auth_url)
    except Exception:
        pass

    input("Нажмите Enter после подтверждения в браузере...")

    session = call("auth.getSession", {"api_key": api_key, "token": token}, api_secret)

    print("\nГотово. Добавьте в .env:")
    print(f"LASTFM_SESSION_KEY={session['session']['key']}")


if __name__ == "__main__":
    main()
