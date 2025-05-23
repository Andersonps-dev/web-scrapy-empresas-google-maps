from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse
import os
import sys
import sqlite3

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from Main import GoogleMapsScraper

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()

    if args.search:
        search_list = [args.search]
    else:
        input_file_path = 'input.txt'
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