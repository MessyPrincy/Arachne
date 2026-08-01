import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

url = "https://books.toscrape.com/"

def fetch_page(url):
    response = requests.get(url)

    response.raise_for_status()

    return response.text

def parse_books(html, url):
    soup = BeautifulSoup(html, "html.parser")

    books = soup.find_all("article", class_="product_pod")

    book_list = []

    for book in books:
        title = book.select_one("h3 a")["title"]
        price = book.find("p", class_="price_color").get_text(strip=True)
        link = urljoin(url, book.select_one("h3 a")["href"])
        book_list.append({"title": title, "price": price, "link" : link})

    return book_list

def get_next_page_url(html, current_url):
    soup = BeautifulSoup(html, "html.parser")

    next_html = soup.find("li", class_="next").select_one("a")["href"]

    return urljoin(current_url, next_html)

def scrape(url, max_pages):
    books = []
    for i in range(max_pages):
        html = fetch_page(url)
        books.append(parse_books(html, url))
        url = get_next_page_url(html, url)

    return books


print(scrape(url, 3))
