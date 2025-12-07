import requests
from bs4 import BeautifulSoup

def scrape_static():
    url = "https://books.toscrape.com/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    books = []

    for item in soup.select(".product_pod"):
        title = item.h3.a["title"]
        price = item.select_one(".price_color").text

        books.append({
            "title": title,
            "price": price
        })

    return books