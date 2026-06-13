import requests
from bs4 import BeautifulSoup

def debug_justwatch_page():
    url = "https://www.justwatch.com/pl/nowe"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "pl-PL,pl;q=0.9",
    }
    
    print("Pobieram stronę do diagnostyki...")
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code != 200:
        print(f"Błąd pobierania! Status: {response.status_code}")
        return
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Wyciągamy nagłówki lub spany, które mogą zawierać daty/teksty typu "Dzisiaj", "Wczoraj" lub "13/06"
    print("\nSzukam tekstów dat w kodzie strony...")
    spans = soup.find_all('span')
    
    found_any = False
    for span in spans:
        txt = span.get_text().strip()
        # Interesują nas słowa kluczowe, po których JustWatch organizuje sekcje
        if any(keyword in txt.lower() for keyword in ["dzisiaj", "wczoraj", "czerwiec", "2026", "nowe"]):
            print(f" -> Znaleziono span z tekstem: '{txt}'")
            found_any = True
            
    if not found_any:
        print("Nie znaleziono żadnych znajomych tekstów dat! Strona może być pusta lub zablokowana przez Cloudflare.")
        
    # Zapiszmy też kawałek surowego body do pliku, żebyś mógł rzucić okiem co tam siedzi
    with open("raw_body.html", "w", encoding="utf-8") as f:
        f.write(response.text)
    print("\nZapisano surowy HTML do pliku 'raw_body.html' w celu dalszej analizy.")

if __name__ == "__main__":
    debug_justwatch_page()