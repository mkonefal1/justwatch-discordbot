import argparse
import json
import os
import re
import time
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

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


def get_justwatch_html_via_headless():
    """Uruchamia ukryte Chromium i przewija pionowo na sam dół strony,

    żeby załadować wszystkie platformy (w tym CDA, HBO, SkyShowtime).
    """
    url = f"{BASE_URL}/pl/nowe"
    print("🌐 Uruchamianie ukrytej przeglądarki Chromium (Headless)...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 1000}
        )
        page = context.new_page()
        
        print(f"⏱️ Ładowanie strony: {url}")
        page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        try:
            page.wait_for_selector("button:has-text('Akceptuję')", timeout=2000)
            page.click("button:has-text('Akceptuję')")
        except Exception:
            pass

        print("🖲️ Przewijanie pionowe w dół w celu dociągnięcia wszystkich platform...")
        last_height = page.evaluate("document.body.scrollHeight")
        
        for _ in range(8):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1.5)
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        html_content = page.content()
        browser.close()
        return html_content


def parse_justwatch_with_counters(html_content):
    """Parsuje wyrenderowany HTML, wyciągając tytuły, liczniki oraz dedykowane slugi platform."""
    if not html_content:
        return None

    soup = BeautifulSoup(html_content, "html.parser")
    today_groups = {}

    time_blocks = soup.select(".timeline__time-block")
    if not time_blocks:
        time_blocks = soup.find_all("div", class_=re.compile(r"time-block|timeframe"))

    if not time_blocks:
        print("❌ Nie znaleziono bloków premier w wyrenderowanym HTML.")
        return None

    today_block = time_blocks[0]
    provider_blocks = today_block.select(".timeline__provider-block") or today_block.find_all("div", class_=re.compile(r"provider-block"))
    
    print(f"📊 Przetwarzanie wyrenderowanych platform (znaleziono: {len(provider_blocks)})...")

    for block in provider_blocks:
        img = block.find("img")
        platform_name = img.get("alt", "Inne platformy").strip() if img else "Inne platformy"
        
        # Ekstrakcja sluga platformy z linku do ikonki logo
        platform_slug = ""
        if img:
            img_src = img.get("src", "") or img.get("data-src", "")
            slug_match = re.search(r'/provider/([^/]+)/', img_src)
            if slug_match:
                platform_slug = slug_match.group(1)
        
        if not platform_slug:
            platform_slug = platform_name.lower().replace(" ", "").replace("+", "plus")

        # Odczyt liczby pozycji z tekstu nagłówka wiersza dostawcy
        total_count = 0
        block_text = block.get_text(separator=" ")
        count_match = re.search(r'(\d+)\s*(?:pozycji|pozycja|pozycje|nowości|nowość|tytuły|tytułów)?', block_text)
        
        if count_match:
            total_count = int(count_match.group(1))

        if platform_name not in today_groups:
            today_groups[platform_name] = {
                "items": [],
                "total_count": total_count,
                "slug": platform_slug
            }
            
        # Zbieranie klikalnych tytułów
        links = block.find_all("a", href=True)
        for link_tag in links:
            href = link_tag["href"]
            if not ("/pl/film/" in href or "/pl/serial/" in href):
                continue
                
            full_link = f"{BASE_URL}{href}" if href.startswith("/") else href
            img_tag = link_tag.find("img")
            
            if img_tag and img_tag.get("alt"):
                title_text = img_tag["alt"].strip()
                item_data = (title_text, full_link)
                
                if item_data not in today_groups[platform_name]["items"]:
                    today_groups[platform_name]["items"].append(item_data)

    return today_groups


def generate_discord_message(grouped_data):
    """Formatowanie wiadomości z wyłączonym generowaniem miniaturek (embeds) w Discordzie."""
    if not grouped_data:
        return f"**Dzisiejsze premiery VOD - {DISPLAY_DATE}**\n\nBrak zarejestrowanych nowości na dzisiaj."

    message_lines = [f"**Dzisiejsze premiery VOD - {DISPLAY_DATE}**"]

    for platform, data in grouped_data.items():
        items = data["items"]
        visible_count = len(items)
        total_reported = max(data["total_count"], visible_count)
        slug = data["slug"]
        
        clean_platform = platform.lower().replace(" ", "").replace("+", "plus")
        
        # Nagłówek sekcji dostawcy
        if total_reported > visible_count:
            message_lines.append(f"\n`/{clean_platform}/` — **{total_reported} pozycji** *(widzisz pierwsze {visible_count})*\n")
        else:
            message_lines.append(f"\n`/{clean_platform}/` — **{visible_count} pozycji**\n")
        
        # Wypisanie tytułów z blokadą miniaturek <link>
        for title, link in items:
            message_lines.append(f"- [{title}](<{link}>)")
            
        # Blokada miniaturek również dla linku zbiorczego
        if total_reported > visible_count:
            all_titles_url = f"https://www.justwatch.com/pl/serwis-streamingowy/{slug}/nowe"
            message_lines.append(f"└─ 🔗 _[[Wyświetl wszystkie na JustWatch...]]({all_titles_url})_")

    return "\n".join(message_lines)


def send_to_discord(message_content, webhook_url):
    """Wysyła tekst raportu na Discorda, dzieląc go na paczki do 2000 znaków."""
    if not webhook_url or webhook_url.startswith("TUTAJ_WKLEJ"):
        print("⚠️ Brak skonfigurowanego Webhooka. Użyj parametru -webhookUpdate <url>.")
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
                print("🚀 Czysty, profesjonalny raport bez miniaturek wylądował na Discorda!")
            else:
                print(f"❌ Błąd wysyłania na Discorda: Status {response.status_code}")
        except Exception as e:
            print(f"❌ Błąd sieciowy: {str(e)}")


if __name__ == "__main__":
    config = load_config()

    parser = argparse.ArgumentParser(
        description="JustWatch Bot - Poranny asystent premier VOD na Discorda.",
        add_help=False,
    )
    parser.add_argument(
        "-h", "--help", action="help",
        help="Pokazuje tę skróconą listę wszystkich dostępnych komend i kończy działanie.",
    )
    parser.add_argument(
        "-webhookUpdate", metavar="URL", type=str,
        help="Zmienia i trwale zapisuje nowy adres URL Webhooka Discorda.",
    )
    parser.add_argument(
        "-test", action="store_true",
        help="Wysyła natychmiastową wiadomość testową o treści 'to wiadomość testowa' na serwer.",
    )

    args = parser.parse_args()

    if args.webhookUpdate:
        config["discord_webhook_url"] = args.webhookUpdate
        save_config(config)
        print("🌐 Nowy Webhook został pomyślnie zaktualizowany.")
    elif args.test:
        print("🧪 Uruchamiam procedurę testową wiadomości...")
        send_to_discord("to wiadomość testowa", config.get("discord_webhook_url"))
    else:
        print(f"🔍 Przełamywanie renderowania pionowego za pomocą Headless Chromium...")
        html = get_justwatch_html_via_headless()
        grouped_premieres = parse_justwatch_with_counters(html)
        discord_report = generate_discord_message(grouped_premieres)
        send_to_discord(discord_report, config.get("discord_webhook_url"))