import csv
from typing import Generator
from urllib.parse import urljoin

import requests
from dataclasses import dataclass, fields
from bs4 import BeautifulSoup, Tag

BASE_URL = "https://quotes.toscrape.com/"


@dataclass
class Quote:
    text: str
    author: str
    tags: list[str]


FIELDS = [field.name for field in fields(Quote)]


def get_quotes() -> Generator:
    count = 1
    while True:
        next_page = urljoin(BASE_URL, f"page/{count}/")
        request = requests.get(next_page)
        if request.status_code != 200:
            break

        soup = BeautifulSoup(request.content, "html.parser")
        quotes = soup.select(".quote")
        if not quotes:
            break

        for quote in quotes:
            yield quote
        count += 1


def parse_quote(quote: Tag) -> Quote:
    return Quote(
        text=quote.select_one(".text").text,
        author=quote.select_one(".author").text,
        tags=[tag.text for tag in quote.select(".tag")]
    )


def make_tuple(quote: Quote) -> tuple:
    return tuple([quote.text, quote.author, quote.tags])


def main(output_csv_path: str) -> None:
    with open(output_csv_path, "w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(FIELDS)

        for quote in get_quotes():
            quote_obj = parse_quote(quote)
            writer.writerow(make_tuple(quote_obj))


if __name__ == "__main__":
    main("quotes.csv")
