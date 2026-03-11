# HTW Saar Grade Tracker

Dieses Python-Script überprüft automatisch die **Leistungsübersicht im HTW SIM-Portal** und sendet eine **Telegram-Nachricht**, sobald eine neue Note eingetragen wurde.

Das Script ist dafür gedacht, regelmäßig (z.B. per Cronjob) ausgeführt zu werden.

---

# Features

- automatischer Login ins HTW SIM Portal
- Download der Leistungsübersicht als PDF
- Extraktion der Noten aus dem PDF
- Vergleich mit vorherigem Stand
- Telegram Benachrichtigung bei neuen Noten
- Headless Browser (läuft ohne sichtbares Fenster)
- Cronjob kompatibel

---

# Projektstruktur

```
noten_scraper/
│
├── script.py
├── README.md
├── requirements.txt
├── .env.example
└── tmp/
    ├── grades.pdf
    └── grades.json
```

---

# Voraussetzungen

- Python **3.10+**
- Google Chrome
---

# Installation

Repository klonen:

```bash
git clone https://github.com/USERNAME/noten_scraper.git
cd noten_scraper
```

Virtuelle Python‑Umgebung erstellen:

```bash
python3 -m venv venv
```

Virtuelle Umgebung aktivieren:

```bash
source venv/bin/activate
```

Python Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

Hinweis: Wenn die Umgebung aktiv ist, beginnt dein Terminalprompt mit `(venv)`.

---

# Environment Variablen

Erstelle eine `.env` Datei im Projektordner.

Beispiel:

```
UNI_USER=dein_hiz_username
UNI_PASSWD=dein_hiz_passwort
TELEGRAM_TOKEN=telegram_bot_token
TELEGRAM_CHAT_ID=deine_chat_id
```

---

# Telegram Bot erstellen

1. Öffne Telegram
2. Suche nach **@BotFather**
3. Erstelle einen neuen Bot

```
/newbot
```

Du bekommst anschließend einen **Bot Token**.

---

# Chat ID herausfinden

Sende deinem Bot eine Nachricht und öffne:

```
https://api.telegram.org/bot<TOKEN>/getUpdates
```

In der Antwort findest du deine **chat_id**.

---

# Script ausführen

Manuell:

```bash
python script.py
```

Beim Start sendet das Script eine **"Started" Nachricht** an Telegram.

---

# Automatische Ausführung (Cronjob)

Beispiel: **alle 3 Stunden**

```bash
crontab -e
```

Eintrag hinzufügen:

```
0 */3 * * * /Users/USERNAME/noten_scraper/venv/bin/python /Users/USERNAME/noten_scraper/script.py
```

Wichtig: Der Cronjob muss das Python aus der virtuellen Umgebung (`venv`) verwenden, sonst findet Python die installierten Pakete nicht.

Bedeutung:

```
Minute 0, alle 3 Stunden
```

Das Script läuft dann um:

```
00:00
03:00
06:00
09:00
12:00
15:00
18:00
21:00
```

---

# Funktionsweise

1. Login in das HTW SIM Portal mit Selenium
2. Navigation zur Leistungsübersicht
3. Download der PDF
4. Extraktion der Noten mit `pdfplumber`
5. Vergleich mit vorherigem Stand (`grades.json`)
6. Telegram Nachricht bei neuen Noten

---

# Beispiel Telegram Nachricht

```
New grade added!
Algorithmen und Datenstrukturen: 1,7
```

---

# Sicherheit

- Zugangsdaten werden nur lokal in `.env` gespeichert
- keine Daten werden extern gespeichert
- keine Speicherung von Passwörtern im Code

---

# Hinweise

Das Script funktioniert nur solange:

- das Layout der Leistungsübersicht gleich bleibt
- das HTW SIM Portal nicht verändert wird
- ChromeDriver wird automatisch über `webdriver-manager` installiert, es ist keine manuelle Installation nötig.

---

# Haftung

Dieses Projekt ist ein **privates Studentenprojekt** und steht in keiner Verbindung zur HTW Saar.

Verwendung auf eigene Verantwortung.
