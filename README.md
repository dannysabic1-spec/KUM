# 🤖 Bosanski Discord Bot

Kompletan Discord bot na bosanskom jeziku — igre, ekonomija, level sistem, moderacija.

---

## 📋 Sve Komande (prefix: `.`)

### 🎮 Igre

| Komanda | Opis | 💵 Nagrada |
|---|---|---|
| `.kaladont` | Lančana igra riječima | +$10 po tačnoj riječi |
| `.kaladont stop` | Zaustavi Kaladont | — |
| `.vjesalo` | Pogađanje skrivene riječi | +$500 za pobjedu |
| `.slovo <x>` | Pogodi slovo u Vješalu | — |
| `.slots [ulog]` | Zavrtiaj bankomat 🎰 | do $5,000 jackpot |
| `.slotinfo` | Tablica dobitaka za Slots | — |
| `.wordle` | Pogodi 5-slovnu bosansku riječ | $500–$1,000 |
| `.pogodi <rijec>` | Pogodi u Wordleu | — |

### 💵 Ekonomija

| Komanda | Opis |
|---|---|
| `.novac` | Pogledaj vlastiti balans |
| `.novac @korisnik` | Balans drugog korisnika |
| `.prenos @korisnik <iznos>` | Pošalji novac drugom korisniku |
| `.bogatasi` | Lista 10 najbogatijih na serveru |
| `.daj @korisnik <iznos>` | ⭐ Samo vlasnik — daj novac |
| `.uzmi @korisnik <iznos>` | ⭐ Samo vlasnik — uzmi novac |
| `.resetnovac @korisnik` | ⭐ Samo vlasnik — resetuj balans |

### 📊 Level Sistem

| Komanda | Opis |
|---|---|
| `.rang` | Tvoj nivo, XP i rang |
| `.rang @korisnik` | Nivo drugog korisnika |
| `.ljestvica` | Top 10 po XP-u |

### 👥 Server Info

| Komanda | Opis |
|---|---|
| `.brojanje` | Detaljna statistika članova |
| `.help` | Sve komande |

### 🔧 Moderacija

| Komanda | Dozvola | Opis |
|---|---|---|
| `.ban @korisnik [razlog]` | Ban Members | Banuj korisnika |
| `.unban <ID>` | Ban Members | Odbanuj po User ID |
| `.kick @korisnik [razlog]` | Kick Members | Izbaci korisnika |
| `.mute @korisnik` | Manage Roles | Ućutaj korisnika |
| `.unmute @korisnik` | Manage Roles | Odućutaj korisnika |
| `.clear <1-100>` | Manage Messages | Obriši poruke |
| `.banovi` | Manage Guild | Lista banova |
| `.banovi @korisnik` | Manage Guild | Banovi jednog korisnika |

---

## 🤖 Automatske Funkcije

| Funkcija | Opis |
|---|---|
| 🚫 **Anti-Invite** | Automatski briše Discord invite linkove |
| 📈 **XP sistem** | +15-35 XP po poruci (cooldown: 60s) |
| 🎉 **Level Up** | Automatska obavijest pri dostizanju novog nivoa |
| ⚠️ **5 Banova** | Na 5+ banova: sve uloge uklonjene, dodijeljena uloga "Kažnjen" |

---

## 🎮 Detalji Igara

### 🎰 Slots
```
╔══════════════════╗
║   ___SLOTS___    ║
╠══════════════════╣
║                  ║
║   🍒  │  🍋  │  7️⃣  ║
║                  ║
╚══════════════════╝
💵 Kum bet 💵 100
and won nothing... :c
```
- Spin animacija u **3 koraka** (svaki bubnj se zaustavlja posebno)
- Minimalni ulog: **$10** | Maksimalni: **$10,000**
- Jackpot: 7️⃣7️⃣7️⃣ = **$5,000**!

### 🔤 Kaladont
- Svaka riječ mora početi s **posljednja 2 slova** prethodne
- Primjer: `Motika` → **KA**men → **EN**ergija → **JA**buka
- Tačna riječ = **+$10**

### 🪢 Vješalo
- 6 pokušaja, ASCII art vješalo
- Pobjeda = **+$500**

### 🟩 Wordle
- Pogodi 5-slovnu bosansku riječ u 6 pokušaja
- 1. pokušaj = **$1,000** | 2. = **$800** | 3+ = **$500**

---

## 🏅 Rangovi (Level Sistem)

| Nivo | Rang |
|---|---|
| 0–4 | 🌱 Početnik |
| 5–9 | ⚔️ Vitez |
| 10–19 | 🥉 Brončani |
| 20–29 | 🥈 Srebrni |
| 30–39 | 🥇 Zlatni |
| 40–49 | 💎 Dijamant |
| 50+ | 👑 Legenda |

---

## 🚀 Pokretanje

### 1. Instaliraj Python 3.10+
https://python.org/downloads

### 2. Instaliraj zavisnosti
```bash
pip install -r requirements.txt
```

### 3. Napravi Discord Bot
1. https://discord.com/developers/applications
2. **New Application** → unesi naziv
3. **Bot** → **Add Bot**
4. Uključi sve **Privileged Gateway Intents**:
   - ✅ **Server Members Intent**
   - ✅ **Message Content Intent**
   - ✅ **Presence Intent**
5. Kopiraj **Token**

### 4. Postavi .env fajl
```bash
cp .env.example .env
```
Otvori `.env` i upiši token:
```
DISCORD_TOKEN=MTxxxxxxxxxxxxx...
```

### 5. Pozovi bota na server
**OAuth2** → **URL Generator**:
- Scopes: `bot`
- Permissions: `Administrator`
- Kopiraj link → otvori u browseru → dodaj na server

### 6. Pokreni
```bash
python bot.py
```

---

## 📁 Struktura

```
discord-bot/
├── bot.py              — Glavni fajl
├── requirements.txt    — Python paketi
├── .env.example        — Primjer env fajla
├── README.md
├── cogs/
│   ├── ekonomija.py    — 💵 Ekonomija sistem
│   ├── kaladont.py     — 🎮 Kaladont igra
│   ├── vjesalo.py      — 🪢 Vješalo igra
│   ├── slots.py        — 🎰 Slot mašina
│   ├── wordle.py       — 🟩 Wordle igra
│   ├── leveling.py     — 📈 Level & XP sistem
│   └── moderation.py   — 🔧 Moderacija & anti-invite
└── data/               — Auto-kreira se (JSON podaci)
    ├── ekonomija.json  — Balans svih korisnika
    ├── leveling.json   — XP i nivo podaci
    └── bans.json       — Ban statistike
```

---

**🇧🇦 Napravljeno za bosansku Discord zajednicu**
