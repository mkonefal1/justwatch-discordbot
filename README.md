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
(Pamiętaj, aby powyższe ścieżki /Users/XXX/... podmienić na realną ścieżkę do Twojego projektu na serwerze, którą sprawdzisz wpisując w terminalu polecenie pwd).