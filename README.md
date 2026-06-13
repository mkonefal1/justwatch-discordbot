# ENG:
# JustWatch Bot - Morning VOD Premiere Assistant 🚀

An automated Python script that fetches today's movie and TV show releases from streaming platforms in Poland via the JustWatch service and sends an aesthetically pleasing, sorted report to a specified Discord channel using a Webhook.

The bot is designed with digital minimalism in mind — reports are stripped of unnecessary rich previews (embeds) to ensure maximum readability.

---

## 🔥 Features and Operational Mechanism

* **Vertical and Horizontal Lazy Loading Bypass:** The script utilizes a headless browser via **Playwright (Headless Chromium)** to physically load the dynamic page content. It crawls down the HTML structure, fetching deeply nested platforms (CDA Premium, SkyShowtime, HBO Max).
* **Smart Counters:** Since JustWatch cuts off very long horizontal lists (carousels) at 10 items, the bot extracts the actual title count for each platform directly from the source code and appends it to the header (e.g., `/bloodstream/ — 245 items`).
* **Dynamic Bulk Links:** If a platform's premiere list is too long and has been truncated by the JustWatch interface, the bot automatically generates a clickable Markdown link below the list, leading directly to that specific provider's full new releases section.
* **No Clutter (No Embeds):** All movie and TV show links are automatically wrapped in angle brackets `<...>`, completely preventing Discord from generating massive image previews and rich embeds.
* **Automatic Chunking:** The script intelligently splits the report into chunks under 2,000 characters, ensuring it never hits Discord's hard API limits.

---

## 🛠️ Installation Guide (Local or VPS Server)

This guide assumes you have Python 3.9 or newer installed on your computer or VPS server (Debian/Ubuntu/Fedora).

### 1. Repository Cloning and Environment Setup
Navigate to the project directory and create an isolated virtual environment `.venv`:
# Create a virtual environment
```bash
python3 -m venv .venv
```

# Activate the environment (macOS / Linux)
```bash
source .venv/bin/activate
```

# Activate the environment (Windows PowerShell)
```bash
.venv\Scripts\Activate.ps1
```

### 2. Install Lightweight Production Dependencies

Install the required packages from the requirements.txt file:
```bash
pip install -r requirements.txt
```

### 3. Install the Playwright Binary Browser

This is a crucial step — without it, the script will not be able to launch the headless Chromium engine:

```bash
playwright install chromium
```

# IF YOU ARE ON A VPS (Ubuntu/Debian) and lack system libraries for the browser, also execute:
```bash
playwright install-deps
```

---

## ⚙️ Configuration and Execution

### 1. First Run and Saving the Webhook
The script stores the Discord webhook URL in a `config.json` file. You can automatically generate and permanently update it using the built-in `-webhookUpdate` flag:

```bash
python3 justwatch_today.py -webhookUpdate "PASTE_YOUR_DISCORD_WEBHOOK_URL_HERE"
```

### 2. Connection Test
To ensure communication with Discord works flawlessly without running the entire JustWatch parser, execute:

```bash
python3 justwatch_today.py -test
```

### 3. Production Run (Full Report)
To fetch today's premieres and send the report to your channel, simply run the script without any parameters:

```bash
python3 justwatch_today.py
```

---

## ⏱️ VPS Automation (Cron)

To have the bot send the report every morning (e.g., at 07:30 AM), it is best to implement it into the system's `cron` task scheduler on your VPS server.

Open the cron task editor:

```bash
crontab -e
```

Append the rule at the very bottom of the file, specifying the **absolute paths** to the Python interpreter inside `.venv` and to the script itself:

```plaintext
30 07 * * * /Users/XXX/.../JustWatch-bot/.venv/bin/python3 /Users/XXX/.../JustWatch-bot/justwatch_today.py > /dev/null 2>&1
```

*(Remember to replace the template paths `/Users/XXX/...` above with the real absolute path to your project on the server, which you can check by typing the `pwd` command in your terminal).*

# PL:

# JustWatch Bot - Poranny Asystent Premier VOD 🚀

Automatyczny skrypt w Pythonie, który pobiera dzisiejsze nowości kinowe i serialowe z platform streamingowych w Polsce za pośrednictwem serwisu JustWatch i wysyła estetyczny, posortowany raport na wskazany kanał Discorda za pomocą Webhooka.

Bot został zaprojektowany z myślą o digital minimizmie — raporty są pozbawione zbędnych miniaturek (embeds), co zapewnia maksymalną czytelność.

---

## 🔥 Funkcje i Mechanizm Działania

* **Pionowy i Poziomy Lazy Loading Bypass:** Skrypt wykorzystuje ukrytą przeglądarkę **Playwright (Headless Chromium)**, aby fizycznie załadować dynamiczną zawartość strony. Wspina się na dół struktury HTML, dociągając głębokie platformy (CDA Premium, SkyShowtime, HBO Max).
* **Inteligentne Liczniki:** Ponieważ JustWatch ucina bardzo długie horyzontalne listy (karuzele) do 10 kafelków, bot wyciąga z kodu źródłowego rzeczywisty licznik pozycji danej platformy i dokleja go do nagłówka (np. `/bloodstream/ — 245 pozycji`).
* **Dynamiczne Linki Zbiorcze:** Jeśli lista premier danej platformy jest za długa i została przycięta przez interfejs JustWatch, bot automatycznie generuje pod listą klikalny odnośnik Markdown prowadzący bezpośrednio do pełnej sekcji nowości danego dostawcy.
* **Brak Śmietnika (No Embeds):** Wszystkie linki do filmów i seriali są automatycznie maskowane w ostre nawiasy `<...>`, co całkowicie blokuje generowanie gigantycznych miniaturek i podglądów na Discordzie.
* **Automatyczny Chunking:** Skrypt inteligentnie dzieli raport na paczki poniżej 2000 znaków, dzięki czemu nigdy nie przekroczy twardych limitów API Discorda.

---

## 🛠️ Instrukcja Instalacji (Lokalnie lub Serwer VPS)

Instrukcja zakłada, że masz zainstalowanego Pythona w wersji 3.9 lub nowszej na swoim komputerze lub serwerze VPS (Debian/Ubuntu/Fedora).

### 1. Klonowanie repozytorium i konfiguracja środowiska
Wejdź do katalogu projektu i utwórz wirtualne środowisko izolowane `.venv`:

```bash
# Tworzenie wirtualnego środowiska
python3 -m venv .venv
```
# Aktywacja środowiska (macOS / Linux)
```bash
source .venv/bin/activate
```
# Aktywacja środowiska (Windows PowerShell)
```bash
.venv\Scripts\Activate.ps1
```

### 2. Instalacja odchudzonych zależności produkcyjnych

Zainstaluj wymagane pakiety z pliku requirements.txt:
```bash
pip install -r requirements.txt
```

### 3. Instalacja binarnej przeglądarki Playwright

To kluczowy krok — bez niego skrypt nie uruchomi ukrytego silnika Chromium:

```Bash
playwright install chromium
```
# JEŚLI JESTEŚ NA VPS (Ubuntu/Debian) i brakuje bibliotek systemowych dla przeglądarki, wykonaj również:
```bash
playwright install-deps
```

## ⚙️ Konfiguracja i Uruchomienie

1. Pierwsze uruchomienie i zapisanie Webhooka
Skrypt przechowuje adres URL webhooka Discorda w pliku config.json. Możesz go automatycznie wygenerować i trwale zaktualizować za pomocą wbudowanej flagi -webhookUpdate:

```Bash
python3 justwatch_today.py -webhookUpdate "TUTAJ_WKLEJ_SWOJ_URL_WEBHOOKA_DISCORDA"
```
2. Test połączenia
Aby upewnić się, że komunikacja z Discordem działa bezbłędnie bez uruchamiania całego parsera JustWatch, wykonaj:

```Bash
python3 justwatch_today.py -test
```
3. Uruchomienie produkcyjne (Pełny Raport)
Aby pobrać dzisiejsze premiery i wysłać raport na kanał, po prostu uruchom skrypt bez żadnych parametrów:

```Bash
python3 justwatch_today.py
```
⏱️ Automatyzacja na VPS (Cron)
Aby bot wysyłał raport codziennie rano (np. o godzinie 07:30), najlepiej zaimplementować go do systemowego harmonogramu zadań cron na serwerze VPS.

Otwórz edytor zadań cron:

```Bash
crontab -e
```
Dopisz regułę na samym dole pliku, wskazując bezwzględne ścieżki do interpretera Pythona wewnątrz .venv oraz do samego skryptu:

```Plaintext
30 07 * * * /Users/XXX/.../JustWatch-bot/.venv/bin/python3 /Users/XXX/.../JustWatch-bot/justwatch_today.py > /dev/null 2>&1
```
*(Pamiętaj, aby powyższe ścieżki /Users/XXX/... podmienić na realną ścieżkę do Twojego projektu na serwerze, którą sprawdzisz wpisując w terminalu polecenie pwd).*