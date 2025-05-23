from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys
import sqlite3

# Classe para armazenar dados de um local
@dataclass
class Business:
    name: str = None
    address: str = None
    website: str = None
    phone_number: str = None
    reviews_count: int = None
    reviews_average: float = None
    latitude: float = None
    longitude: float = None
    cidade: str = None
    pesquisa: str = None
    estado: str = None

@dataclass
class BusinessList:
    business_list: list[Business] = field(default_factory=list)

    def dataframe(self):
        return pd.json_normalize((asdict(business) for business in self.business_list), sep="_")

    def save_to_sqlite(self, db_name="dados_google_maps.db", table_name="negocios"):
        df = self.dataframe()
        conn = sqlite3.connect(db_name)
        df.to_sql(table_name, conn, if_exists='append', index=False)
        conn.close()

def extract_coordinates_from_url(url: str) -> tuple[float, float]:
    coordinates = url.split('/@')[-1].split('/')[0]
    return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

def split_search_term(term: str) -> tuple[str, str, str]:
    """Separar 'Salão de beleza - São Paulo - SP' em ('Salão de beleza', 'São Paulo', 'SP')"""
    parts = [p.strip() for p in term.strip().split('-')]
    pesquisa = parts[0] if len(parts) > 0 else ""
    cidade = parts[1] if len(parts) > 1 else ""
    estado = parts[2] if len(parts) > 2 else ""
    return pesquisa, cidade, estado

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()

    if args.search:
        search_list = [args.search]
    else:
        input_file_path = os.path.join(os.getcwd(), 'input.txt')
        if os.path.exists(input_file_path):
            with open(input_file_path, 'r', encoding='utf-8') as file:
                search_list = file.readlines()
        else:
            print("Arquivo input.txt não encontrado e nenhum argumento -s foi passado.")
            sys.exit()

    total = args.total if args.total else 1_000_000

    with sync_playwright() as p:
        for search_for_index, search_for in enumerate(search_list):
            search_for = search_for.strip()
            if not search_for:
                continue

            pesquisa, cidade, estado = split_search_term(search_for)
            print(f"-----\n{search_for_index} - {search_for}")

            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://www.google.com/maps", timeout=60000)
            page.wait_for_timeout(2000)

            page.locator('//input[@id="searchboxinput"]').fill(search_for)
            page.wait_for_timeout(1000)
            page.keyboard.press("Enter")
            page.wait_for_timeout(2000)

            page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

            previously_counted = 0
            while True:
                page.mouse.wheel(0, 50000)
                page.wait_for_timeout(1500)  # Reduzido

                count = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
                if count >= total:
                    listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                    listings = [listing.locator("xpath=..") for listing in listings]
                    print(f"Total Scraped: {len(listings)}")
                    break
                else:
                    if count == previously_counted:
                        listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                        print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                        break
                    else:
                        previously_counted = count
                        print(f"Currently Scraped: {count}")

            business_list = BusinessList()

            for listing in listings:
                try:
                    listing.click()
                    page.wait_for_timeout(1200)

                    business = Business()
                    try:
                        business.name = listing.get_attribute('aria-label') or ""
                    except: business.name = ""
                    try:
                        business.address = page.locator('//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]').first.inner_text()
                    except: business.address = ""
                    try:
                        business.website = page.locator('//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]').first.inner_text()
                    except: business.website = ""
                    try:
                        business.phone_number = page.locator('//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]').first.inner_text()
                    except: business.phone_number = ""
                    try:
                        review_text = page.locator('//button[@jsaction="pane.reviewChart.moreReviews"]//span').first.inner_text()
                        business.reviews_count = int(review_text.split()[0].replace(',', '').strip())
                    except: business.reviews_count = ""
                    try:
                        avg_text = page.locator('//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]').first.get_attribute('aria-label')
                        business.reviews_average = float(avg_text.split()[0].replace(',', '.').strip())
                    except: business.reviews_average = ""
                    try:
                        business.latitude, business.longitude = extract_coordinates_from_url(page.url)
                    except: business.latitude, business.longitude = "", ""

                    business.cidade = cidade
                    business.pesquisa = pesquisa
                    business.estado = estado

                    business_list.business_list.append(business)
                except Exception as e:
                    print(f"Erro ao coletar dados de um item: {e}")

            business_list.save_to_sqlite()
            browser.close()

if __name__ == "__main__":
    main()