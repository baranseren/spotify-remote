"""
Spotify OAuth - Tek seferlik yetkilendirme.
Tarayici acilacak, Spotify'a giris yap, otomatik token kaydedilecek.
"""

import json
import os
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import spotipy
from spotipy.oauth2 import SpotifyOAuth

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spotify_config.json")
CACHE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".spotify_cache")

with open(CONFIG_FILE, "r") as f:
    config = json.load(f)

auth_manager = SpotifyOAuth(
    client_id=config["client_id"],
    client_secret=config["client_secret"],
    redirect_uri=config["redirect_uri"],
    scope="user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-read",
    cache_path=CACHE_PATH
)

auth_code = None

class CallbackHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = parse_qs(urlparse(self.path).query)
        if "code" in query:
            auth_code = query["code"][0]
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><h1>Basarili! Bu sekmeyi kapatabilirsin.</h1></body></html>".encode("utf-8"))
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write("<html><body><h1>Hata olustu</h1></body></html>".encode("utf-8"))

    def log_message(self, format, *args):
        pass


# Token zaten varsa kullan
token_info = auth_manager.cache_handler.get_cached_token()
if token_info and not auth_manager.is_token_expired(token_info):
    print("Token zaten mevcut ve gecerli!")
    sp = spotipy.Spotify(auth_manager=auth_manager)
    user = sp.current_user()
    print(f"Giris yapan: {user['display_name']}")
else:
    # Tarayici ac
    auth_url = auth_manager.get_authorize_url()
    print(f"Tarayici aciliyor...")
    webbrowser.open(auth_url)

    # Callback bekle
    print("Spotify girisini bekliyor...")
    server = HTTPServer(("127.0.0.1", 8888), CallbackHandler)
    server.handle_request()

    if auth_code:
        token_info = auth_manager.get_access_token(auth_code)
        print("Token kaydedildi!")

        sp = spotipy.Spotify(auth_manager=auth_manager)
        user = sp.current_user()
        print(f"Giris yapan: {user['display_name']}")
        print("Artik spotify_kontrol.py ile sarki arayip calabilirsin!")
    else:
        print("Yetkilendirme basarisiz!")
