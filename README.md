# Spotify Kontrol Sistemi - Dokumantasyon

## Genel Bakis

Bu sistem Python ile Spotify'i uzaktan kontrol etmeni saglar. Iki katmanli calisir:

1. **Media Key Katmani** - API gerektirmez, Windows media tuslarini simule eder
2. **Spotipy API Katmani** - Spotify Web API uzerinden tam kontrol saglar (sarki arama, belirli sarki calma, ses ayari vb.)

---

## Dosya Yapisi

```
C:\Users\baranseren\Desktop\
  spotify_kontrol.py      -> Ana kontrol scripti (hem media key hem API)
  spotify_auth.py          -> Tek seferlik OAuth yetkilendirme scripti
  spotify_config.json      -> API kimlik bilgileri (Client ID, Secret)
  .spotify_cache           -> OAuth token cache (otomatik olusur)
```

---

## Gereksinimler

- Python 3.12+
- spotipy kutuphanesi (`pip install spotipy`)
- Spotify Premium hesabi (API ile playback kontrolu icin)
- Spotify Desktop uygulamasi (media key icin acik olmali)

---

## Ilk Kurulum (Sifirdan Yapilacaksa)

### Adim 1: spotipy Kur

```bash
pip install spotipy
```

### Adim 2: Spotify Developer App Olustur

1. https://developer.spotify.com/dashboard adresine git
2. Spotify hesabinla giris yap
3. "Create App" tikla
4. App Name: istedigin isim (orn. "Baran Remote")
5. App Description: istedigin aciklama
6. Redirect URI: `http://127.0.0.1:8888/callback` yaz (ONEMLI: localhost degil, 127.0.0.1 olmali!)
7. "Save" tikla
8. Olusturduktan sonra Settings'e gir
9. **Client ID** ve **Client Secret** degerlerini kopyala

### Adim 3: Config Dosyasini Olustur

`spotify_config.json` dosyasini masaustunde olustur:

```json
{
  "client_id": "BURAYA_CLIENT_ID",
  "client_secret": "BURAYA_CLIENT_SECRET",
  "redirect_uri": "http://127.0.0.1:8888/callback"
}
```

### Adim 4: Yetkilendirme Yap (Tek Seferlik)

```bash
python spotify_auth.py
```

- Tarayici acilacak, Spotify hesabinla giris yap
- "Kabul Et / Agree" tikla
- Tarayicide "Basarili!" yazisini gorursun
- Terminal'de "Token kaydedildi!" mesaji cikar
- `.spotify_cache` dosyasi otomatik olusur, bir daha giris yapman gerekmez

### Adim 5: Test Et

```bash
python spotify_kontrol.py nowplaying
python spotify_kontrol.py search Tarkan
```

---

## Komut Satiri Kullanimi (CLI)

### Media Key Komutlari (API Gerektirmez)

| Komut | Aciklama |
|-------|----------|
| `python spotify_kontrol.py play` | Muzigi baslat/duraklat (toggle) |
| `python spotify_kontrol.py next` | Sonraki sarkiya gec |
| `python spotify_kontrol.py prev` | Onceki sarkiya don |
| `python spotify_kontrol.py vup` | Sistem sesini 5 kademe artir (~%10) |
| `python spotify_kontrol.py vdown` | Sistem sesini 5 kademe azalt (~%10) |
| `python spotify_kontrol.py mute` | Sesi kapat/ac (toggle) |

**Not:** Media key komutlari Spotify acik oldugu surece calisir. API baglantisi gerektirmez.

### API Komutlari (Spotify Premium + Yetkilendirme Gerekir)

| Komut | Aciklama |
|-------|----------|
| `python spotify_kontrol.py search Tarkan Dudu` | Sarki arayip direkt cal |
| `python spotify_kontrol.py find Sezen Aksu` | Sarki ara, 5 sonuc listele (calmaz) |
| `python spotify_kontrol.py nowplaying` | Su an calan sarkiyi goster |
| `python spotify_kontrol.py vol 75` | Spotify ses seviyesini %75 yap (0-100) |
| `python spotify_kontrol.py devices` | Aktif Spotify cihazlarini listele |

### Ornekler

```bash
# Tarkan'dan bir sarki bul ve cal
python spotify_kontrol.py search Tarkan

# Belirli bir sarki ara ve cal
python spotify_kontrol.py search "Sezen Aksu Geri Don"

# Sarkiyi duraklat
python spotify_kontrol.py play

# Sonraki sarki
python spotify_kontrol.py next

# Sesi %50 yap
python spotify_kontrol.py vol 50

# Su an ne caliyor?
python spotify_kontrol.py nowplaying

# "Manga" ara, sonuclari listele
python spotify_kontrol.py find Manga

# Cihazlari gor
python spotify_kontrol.py devices
```

---

## Python'dan Import Ederek Kullanim

Script'i baska Python projelerinden import edebilirsin:

```python
import spotify_kontrol as sp

# === Media Key (API gerektirmez) ===
sp.play_pause()           # Baslat/duraklat
sp.next_track()           # Sonraki sarki
sp.prev_track()           # Onceki sarki
sp.volume_up(5)           # 5 kademe ses ac
sp.volume_down(3)         # 3 kademe ses kis
sp.mute()                 # Mute toggle

# === API ile (Yetkilendirme gerekir) ===
sp.search_and_play("Tarkan Dudu")      # Ara ve cal
sp.search_tracks("Sezen Aksu", 5)      # 5 sonuc listele (dict listesi doner)
sp.play_uri("spotify:track:xxx")       # URI ile belirli sarki cal
sp.current_track()                      # Su an calani goster (dict doner)
sp.set_volume(80)                       # Ses %80
sp.get_devices()                        # Cihaz listesi (dict listesi doner)
sp.shuffle(True)                        # Karistirma ac
sp.shuffle(False)                       # Karistirma kapat
sp.repeat("track")                      # Tekrar modu: track, context, off
```

### Fonksiyon Detaylari

#### `search_and_play(query)` -> str
Verilen sorguyu arar, ilk sonucu calar. Donen string: "Caliniyor: Sarki Adi - Sanatci"

#### `search_tracks(query, limit=5)` -> list
Sonuclari dict listesi olarak doner:
```python
[
  {"no": 1, "name": "Dudu", "artist": "Tarkan", "uri": "spotify:track:xxx"},
  {"no": 2, "name": "Simarik", "artist": "Tarkan", "uri": "spotify:track:yyy"},
]
```

#### `current_track()` -> dict
```python
{
  "name": "Dudu",
  "artist": "Tarkan",
  "album": "Karma",
  "is_playing": True,
  "progress_ms": 45000,
  "duration_ms": 234000
}
```

#### `get_devices()` -> list
```python
[
  {"name": "BARAN-PC", "type": "Computer", "id": "abc123", "active": True}
]
```

---

## Token Suresi ve Yenileme

- OAuth token **1 saat** gecerlidir
- spotipy token suresi dolunca **otomatik yeniler** (refresh token `.spotify_cache` icinde saklanir)
- `.spotify_cache` dosyasini silersen tekrar `spotify_auth.py` calistirman gerekir
- Normal kullanida bir daha yetkilendirme yapman gerekmez

---

## Sorun Giderme

### "API baglantisi yok" hatasi
- `spotify_config.json` dosyasi masaustunde mi kontrol et
- `.spotify_cache` dosyasi var mi kontrol et, yoksa `python spotify_auth.py` calistir

### "No active device" hatasi
- Spotify Desktop uygulamasinin acik oldugunu kontrol et
- Spotify'da en az bir sarki calmis ol (ilk acilista aktif device olmayabilir)
- `python spotify_kontrol.py devices` ile cihazlari kontrol et

### "Premium required" hatasi
- Playback kontrolu (play, pause, skip, volume) Spotify Premium gerektirir
- Free hesapla sadece `search_tracks`, `current_track`, `get_devices` calisir

### Token suresi dolmus
- Normalde otomatik yenilenir
- Yenilenmiyorsa `.spotify_cache` dosyasini sil ve `python spotify_auth.py` tekrar calistir

### Media key calismiyorsa
- Spotify Desktop uygulamasinin acik oldugunu kontrol et
- Baska bir media player (VLC, YouTube vb.) medya tuslarini kapmiyor mu kontrol et

---

## Spotify Developer Dashboard

- URL: https://developer.spotify.com/dashboard
- Mevcut App: Baran Remote (veya olusturdugum isim)
- Redirect URI: `http://127.0.0.1:8888/callback`
- Scopes: `user-modify-playback-state`, `user-read-playback-state`, `user-read-currently-playing`, `user-library-read`

---

## Claude Code ile Kullanim

Claude Code bu script'i dogrudan calistirabiliyor. Telegram veya dogrudan sohbetten su komutlari verebilirsin:

- "Tarkan cal" -> `python spotify_kontrol.py search Tarkan`
- "sonraki sarki" -> `python spotify_kontrol.py next`
- "sesi kis" -> `python spotify_kontrol.py vdown`
- "ne caliyor" -> `python spotify_kontrol.py nowplaying`
- "spotify ac" -> `start spotify:` + play komutu

---

*Olusturma Tarihi: 22 Mart 2026*
*Kutuphane: spotipy 2.26.0*
*Python: 3.12*
