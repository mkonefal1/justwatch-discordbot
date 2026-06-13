import argparse
import json
import os
import re
from datetime import datetime
import requests
from bs4 import BeautifulSoup

# Konfiguracja ścieżek i stałych
BASE_URL = "https://www.justwatch.com"
DISPLAY_DATE = datetime.now().strftime("%d/%m/%Y")
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")


def load_config():
    """Wczytuje konfigurację (webhook) z pliku config.json lub tworzy domyślny."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"discord_webhook_url": "TUTAJ_WKLEJ_SWÓJ_ADRES_URL_WEBHOOKA"}


def save_config(config_data):
    """Zapisuje aktualną konfigurację do pliku config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=4)
        print(f"✅ Konfiguracja została pomyślnie zapisana w: {CONFIG_FILE}")
    except Exception as e:
        print(f"❌ Błąd podczas zapisywania konfiguracji: {str(e)}")


def get_justwatch_html():
    """Pobiera kod HTML ze strony z nowościami JustWatch."""
    url = f"{BASE_URL}/pl/nowe"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9",
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Błąd podczas pobierania strony JustWatch: {str(e)}")
        return None


def parse_justwatch_ssr_data(html_content):
    """Parsuje HTML, wyciąga dzisiejsze premiery oraz ich bezpośrednie linki URL."""
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")
    today_groups = {}

    time_blocks = soup.select(".timeline__time-block")
    if not time_blocks:
        time_blocks = soup.find_all(
            "div", class_=re.compile(r"time-block|timeframe")
        )

    if not time_blocks:
        print("❌ Brak bloków premier w kodzie HTML.")
        return None

    # Bierzemy pierwszy blok (indeks 0), czyli sekcję "Dzisiaj"
    today_block = time_blocks[0]
    provider_blocks = today_block.select(
        ".timeline__provider-block"
    ) or today_block.find_all("div", class_=re.compile(r"provider-block"))

    for block in provider_blocks:
        img = block.find("img")
        platform_name = (
            img.get("alt", "Inne platformy").strip()
            if img
            else "Inne platformy"
        )

        if platform_name not in today_groups:
            today_groups[platform_name] = []

        links = block.find_all("a", href=True)

        for link_tag in links:
            href = link_tag["href"]
            if not ("/pl/film/" in href or "/pl/serial/" in href):
                continue

            full_link = f"{BASE_URL}{href}" if href.startswith("/") else href
            img_tag = link_tag.find("img", class_="picture-comp__img")

            if img_tag and img_tag.get("alt"):
                title_text = img_tag["alt"].strip()
                item_data = (title_text, full_link)

                if item_data not in today_groups[platform_name]:
                    today_groups[platform_name].append(item_data)

    return today_groups


def generate_discord_message(grouped_titles):
    """Formatowanie wiadomości w schemat z hiperlinkami Markdown dla Discorda."""
    if not grouped_titles:
        return f"**Dzisiejsze premiery VOD - {DISPLAY_DATE}**\n\nBrak zarejestrowanych nowości na dzisiaj."

    message_lines = [f"**Dzisiejsze premiery VOD - {DISPLAY_DATE}**"]

    for platform, items in grouped_titles.items():
        clean_platform = (
            platform.lower().replace(" ", "").replace("+", "plus")
        )
        message_lines.append(f"\n`/{clean_platform}/`")

        for title, link in items:
            message_lines.append(f"- [{title}]({link})")

    return "\n".join(message_lines)


def send_to_discord(message_content, webhook_url):
    """Wysyła tekst raportu na Discorda, automatycznie dzieląc go na paczki do 2000 znaków."""
    if not webhook_url or webhook_url.startswith("TUTAJ_WKLEJ"):
        print(
            "⚠️ Brak skonfigurowanego Webhooka. Użyj parametru -webhookUpdate <url>, aby go ustawić."
        )
        return

    lines = message_content.split("\n")
    current_chunk = []
    current_length = 0

    for line in lines:
        if current_length + len(line) + 1 > 1900:
            payload = {"content": "\n".join(current_chunk)}
            try:
                requests.post(webhook_url, json=payload, timeout=10)
            except Exception as e:
                print(f"❌ Błąd sieciowy: {str(e)}")
            current_chunk = []
            current_length = 0

        current_chunk.append(line)
        current_length += len(line) + 1

    if current_chunk:
        payload = {"content": "\n".join(current_chunk)}
        try:
            response = requests.post(webhook_url, json=payload, timeout=10)
            if response.status_code == 204:
                print(
                    "🚀 Wiadomość została pomyślnie wysłana na serwer Discord!"
                )
            else:
                print(
                    f"❌ Błąd wysyłania na Discorda: Status {response.status_code}"
                )
        except Exception as e:
            print(f"❌ Błąd sieciowy: {str(e)}")


if __name__ == "__main__":
    # Wczytujemy zapisaną konfigurację
    config = load_config()

    # Definiujemy parser flag CLI
    parser = argparse.ArgumentParser(
        description="JustWatch Bot - Poranny asystent premier VOD na Discorda.",
        add_help=False,  # Wyłączamy domyślne -h, aby zdefiniować własne, skrócone
    )

    # Dodajemy Twoje parametry
    parser.add_argument(
        "-h",
        "--help",
        action="help",
        help="Pokazuje tę skróconą listę wszystkich dostępnych komend i kończy działanie.",
    )
    parser.add_argument(
        "-webhookUpdate",
        metavar="URL",
        type=str,
        help="Zmienia i trwale zapisuje nowy adres URL Webhooka Discorda.",
    )
    parser.add_argument(
        "-test",
        action="store_true",
        help="Wysyła natychmiastową wiadomość testową o treści 'to wiadomość testowa' na serwer.",
    )

    args = parser.parse_args()

    # 1. Obsługa flagi -webhookUpdate
    if args.webhookUpdate:
        config["discord_webhook_url"] = args.webhookUpdate
        save_config(config)
        print("🌐 Nowy Webhook został pomyślnie zaktualizowany.")

    # 2. Obsługa flagi -test
    elif args.test:
        print("🧪 Uruchamiam procedurę testową wiadomości...")
        send_to_discord("to wiadomość testowa", config["discord_webhook_url"])

    # 3. Domyślne uruchomienie (np. rano z crona bez parametrów)
    else:
        print(f"🔍 Pobieranie i przetwarzanie nowości JustWatch...")
        html = get_justwatch_html()
        grouped_premieres = parse_justwatch_ssr_data(html)
        discord_report = generate_discord_message(grouped_premieres)
        send_to_discord(discord_report, config["discord_webhook_url"])