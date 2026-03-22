"""
Spotify Kontrol Modulu
- Media Key ile: API gerektirmez, aninda calisir (play/pause, next, prev, volume)
- Spotipy ile: Sarki arama, belirli sarki calma, playlist yonetimi (API key gerekir)
"""

import ctypes
import time
import sys
import os
import json

# ========== MEDIA KEY KONTROL (API GEREKTIRMEZ) ==========

user32 = ctypes.WinDLL('user32', use_last_error=True)

VK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_VOLUME_UP = 0xAF
VK_VOLUME_DOWN = 0xAE
VK_VOLUME_MUTE = 0xAD

KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002


def _press_key(vk_code):
    user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY, 0)
    time.sleep(0.05)
    user32.keybd_event(vk_code, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)


def play_pause():
    """Muzigi baslat/duraklat"""
    _press_key(VK_MEDIA_PLAY_PAUSE)
    return "Play/Pause gonderildi"


def next_track():
    """Sonraki sarki"""
    _press_key(VK_MEDIA_NEXT_TRACK)
    return "Sonraki sarkiya gecildi"


def prev_track():
    """Onceki sarki"""
    _press_key(VK_MEDIA_PREV_TRACK)
    return "Onceki sarkiya donuldu"


def volume_up(steps=1):
    """Sesi ac (her step ~2%)"""
    for _ in range(steps):
        _press_key(VK_VOLUME_UP)
        time.sleep(0.05)
    return f"Ses {steps} kademe artirildi"


def volume_down(steps=1):
    """Sesi kis (her step ~2%)"""
    for _ in range(steps):
        _press_key(VK_VOLUME_DOWN)
        time.sleep(0.05)
    return f"Ses {steps} kademe azaltildi"


def mute():
    """Sesi kapat/ac"""
    _press_key(VK_VOLUME_MUTE)
    return "Mute toggle"


# ========== SPOTIPY KONTROL (API GEREKIR) ==========

CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spotify_config.json")

_sp = None


def _get_spotify():
    """Spotipy client dondur, yoksa olustur"""
    global _sp
    if _sp is not None:
        return _sp

    if not os.path.exists(CONFIG_FILE):
        print("HATA: spotify_config.json bulunamadi!")
        print("Olusturmak icin: spotify_setup() fonksiyonunu cagir")
        return None

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)

    try:
        import spotipy
        from spotipy.oauth2 import SpotifyOAuth

        cache_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".spotify_cache")
        _sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=config["client_id"],
            client_secret=config["client_secret"],
            redirect_uri=config.get("redirect_uri", "http://127.0.0.1:8888/callback"),
            scope="user-modify-playback-state user-read-playback-state user-read-currently-playing user-library-read",
            cache_path=cache_path,
            open_browser=False
        ))
        return _sp
    except Exception as e:
        print(f"Spotify baglanti hatasi: {e}")
        return None


def spotify_setup(client_id, client_secret, redirect_uri="http://localhost:8888/callback"):
    """API bilgilerini kaydet"""
    config = {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri
    }
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)
    print("Spotify API bilgileri kaydedildi: spotify_config.json")
    print("Ilk kullanimda tarayici acilacak, Spotify hesabinla giris yap.")
    return True


def search_and_play(query):
    """Sarki ara ve cal"""
    sp = _get_spotify()
    if not sp:
        return "API baglantisi yok"

    results = sp.search(q=query, type="track", limit=1)
    if not results['tracks']['items']:
        return f"'{query}' bulunamadi"

    track = results['tracks']['items'][0]
    track_name = track['name']
    artist = track['artists'][0]['name']

    try:
        sp.start_playback(uris=[track['uri']])
        return f"Caliniyor: {track_name} - {artist}"
    except Exception as e:
        return f"Calma hatasi: {e}"


def search_tracks(query, limit=5):
    """Sarki ara, sonuclari listele"""
    sp = _get_spotify()
    if not sp:
        return "API baglantisi yok"

    results = sp.search(q=query, type="track", limit=limit)
    tracks = []
    for i, item in enumerate(results['tracks']['items']):
        tracks.append({
            "no": i + 1,
            "name": item['name'],
            "artist": item['artists'][0]['name'],
            "uri": item['uri']
        })
    return tracks


def play_uri(uri):
    """Belirli bir sarki URI'si cal"""
    sp = _get_spotify()
    if not sp:
        return "API baglantisi yok"

    try:
        sp.start_playback(uris=[uri])
        return "Caliniyor"
    except Exception as e:
        return f"Hata: {e}"


def current_track():
    """Su an calan sarkiyi goster"""
    sp = _get_spotify()
    if not sp:
        return "API baglantisi yok"

    try:
        current = sp.current_playback()
        if not current or not current.get('item'):
            return "Su an hicbir sey calmiyor"

        track = current['item']
        return {
            "name": track['name'],
            "artist": track['artists'][0]['name'],
            "album": track['album']['name'],
            "is_playing": current['is_playing'],
            "progress_ms": current['progress_ms'],
            "duration_ms": track['duration_ms']
        }
    except Exception as e:
        return f"Hata: {e}"


def set_volume(level):
    """Ses seviyesi ayarla (0-100) - API ile"""
    sp = _get_spotify()
    if not sp:
        return "API baglantisi yok"

    try:
        sp.volume(int(level))
        return f"Ses seviyesi: {level}"
    except Exception as e:
        return f"Hata: {e}"


def get_devices():
    """Aktif Spotify cihazlarini listele"""
    sp = _get_spotify()
    if not sp:
        return "API baglantisi yok"

    try:
        devices = sp.devices()
        return [{"name": d['name'], "type": d['type'], "id": d['id'], "active": d['is_active']}
                for d in devices['devices']]
    except Exception as e:
        return f"Hata: {e}"


def shuffle(state=True):
    """Karistirma ac/kapat"""
    sp = _get_spotify()
    if not sp:
        return "API baglantisi yok"

    try:
        sp.shuffle(state)
        return f"Shuffle: {'Acik' if state else 'Kapali'}"
    except Exception as e:
        return f"Hata: {e}"


def repeat(mode="off"):
    """Tekrar modu: track, context, off"""
    sp = _get_spotify()
    if not sp:
        return "API baglantisi yok"

    try:
        sp.repeat(mode)
        return f"Repeat: {mode}"
    except Exception as e:
        return f"Hata: {e}"


# ========== CLI KULLANIM ==========

if __name__ == "__main__":
    komutlar = {
        "play": play_pause,
        "next": next_track,
        "prev": prev_track,
        "vup": lambda: volume_up(5),
        "vdown": lambda: volume_down(5),
        "mute": mute,
    }

    if len(sys.argv) < 2:
        print("Kullanim: python spotify_kontrol.py [komut]")
        print("Media Key Komutlar: play, next, prev, vup, vdown, mute")
        print("API Komutlar: search [sorgu], nowplaying, devices, vol [0-100]")
        sys.exit(0)

    cmd = sys.argv[1].lower()

    if cmd in komutlar:
        print(komutlar[cmd]())
    elif cmd == "search" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        result = search_and_play(query)
        print(result)
    elif cmd == "find" and len(sys.argv) > 2:
        query = " ".join(sys.argv[2:])
        results = search_tracks(query)
        if isinstance(results, list):
            for t in results:
                print(f"  {t['no']}. {t['name']} - {t['artist']}")
        else:
            print(results)
    elif cmd == "nowplaying":
        result = current_track()
        if isinstance(result, dict):
            print(f"  {result['name']} - {result['artist']}")
            print(f"  Album: {result['album']}")
            status = "Caliniyor" if result['is_playing'] else "Duraklatildi"
            print(f"  Durum: {status}")
        else:
            print(result)
    elif cmd == "devices":
        result = get_devices()
        if isinstance(result, list):
            for d in result:
                active = " [AKTIF]" if d['active'] else ""
                print(f"  {d['name']} ({d['type']}){active}")
        else:
            print(result)
    elif cmd == "vol" and len(sys.argv) > 2:
        print(set_volume(sys.argv[2]))
    elif cmd == "setup" and len(sys.argv) > 3:
        spotify_setup(sys.argv[2], sys.argv[3])
    else:
        print(f"Bilinmeyen komut: {cmd}")
