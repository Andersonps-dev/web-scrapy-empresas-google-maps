from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys
import sqlite3

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

class GoogleMapsScraper:
    def __init__(self):
        self.business_list = BusinessList()

    @staticmethod
    def extract_coordinates_from_url(url: str) -> tuple[float, float]:
        coordinates = url.split('/@')[-1].split('/')[0]
        return float(coordinates.split(',')[0]), float(coordinates.split(',')[1])

    @staticmethod
    def split_search_term(term: str) -> tuple[str, str, str]:
        """Separar 'Salão de beleza - São Paulo - SP' em ('Salão de beleza', 'São Paulo', 'SP')"""
        if '-' in term:
            parts = [p.strip() for p in term.strip().split('-')]
            pesquisa = parts[0] if len(parts) > 0 else ""
            cidade = parts[1] if len(parts) > 1 else ""
            estado = parts[2] if len(parts) > 2 else ""
        else:
            pesquisa = term.strip()
            cidade = ""
            estado = ""
        return pesquisa, cidade, estado

    def run(self, search_list, total):
        with sync_playwright() as p:
            for search_for_index, search_for in enumerate(search_list):
                search_for = search_for.strip()
                if not search_for:
                    continue

                pesquisa, cidade, estado = self.split_search_term(search_for)
                print(f"-----\n{search_for_index} - {search_for}")

                browser = p.chromium.launch(headless=False)
                page = browser.new_page()
                page.goto("https://www.google.com/maps", timeout=60000)
                page.wait_for_timeout(5000)

                page.locator('//input[@id="searchboxinput"]').fill(search_for)
                page.wait_for_timeout(3000)
                page.keyboard.press("Enter")
                page.wait_for_timeout(5000)

                page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

                previously_counted = 0
                while True:
                    page.mouse.wheel(0, 50000)
                    page.wait_for_timeout(5000)

                    if page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count() >= total:
                        listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                        listings = [listing.locator("xpath=..") for listing in listings]
                        print(f"Total Scraped: {len(listings)}")
                        break
                    else:
                        current_count = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
                        if current_count == previously_counted:
                            listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                            print(f"Arrived at all available\nTotal Scraped: {len(listings)}")
                            break
                        else:
                            previously_counted = current_count
                            print(f"Currently Scraped: {current_count}")

                for listing in listings:
                    try:
                        listing.click()
                        page.wait_for_timeout(5000)

                        name_attibute = 'aria-label'
                        address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
                        website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
                        phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
                        review_count_xpath = '//button[@jsaction="pane.reviewChart.moreReviews"]//span'
                        reviews_average_xpath = '//div[@jsaction="pane.reviewChart.moreReviews"]//div[@role="img"]'

                        business = Business()
                        business.name = listing.get_attribute(name_attibute) or ""
                        business.address = page.locator(address_xpath).all()[0].inner_text() if page.locator(address_xpath).count() > 0 else ""
                        business.website = page.locator(website_xpath).all()[0].inner_text() if page.locator(website_xpath).count() > 0 else ""
                        business.phone_number = page.locator(phone_number_xpath).all()[0].inner_text() if page.locator(phone_number_xpath).count() > 0 else ""
                        business.reviews_count = int(page.locator(review_count_xpath).inner_text().split()[0].replace(',', '').strip()) if page.locator(review_count_xpath).count() > 0 else ""
                        business.reviews_average = float(page.locator(reviews_average_xpath).get_attribute(name_attibute).split()[0].replace(',', '.').strip()) if page.locator(reviews_average_xpath).count() > 0 else ""
                        business.latitude, business.longitude = self.extract_coordinates_from_url(page.url)
                        business.cidade = cidade
                        business.pesquisa = pesquisa
                        business.estado = estado

                        self.business_list.business_list.append(business)
                    except Exception as e:
                        print(f"Erro ao coletar dados de um item: {e}")

                self.business_list.save_to_sqlite()
                browser.close()

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

    scraper = GoogleMapsScraper()
    scraper.run(search_list, total)

if __name__ == "__main__":
    main()