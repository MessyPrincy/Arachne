from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Any, Optional
from app.base_scraper import BaseScraper

class BooksToScrapeScraper(BaseScraper):
    @classmethod
    def get_name(cls) -> str:
        return "books_to_scrape"

    def parse_books(self, html: str, url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        books = soup.find_all("article", class_="product_pod")
        book_list = []

        for book in books:
            title_elem = book.select_one("h3 a")
            if not title_elem:
                continue
            title = title_elem.get("title", "")
            
            price_elem = book.find("p", class_="price_color")
            price = price_elem.get_text(strip=True) if price_elem else ""
            
            link = urljoin(url, title_elem.get("href", ""))
            book_list.append({"title": title, "price": price, "link": link})

        return book_list

    def get_next_page_url(self, html: str, current_url: str) -> Optional[str]:
        soup = BeautifulSoup(html, "html.parser")
        next_li = soup.find("li", class_="next")
        if not next_li:
            return None
        
        next_a = next_li.select_one("a")
        if not next_a:
            return None
            
        next_html = next_a.get("href")
        if not next_html:
            return None
            
        return urljoin(current_url, next_html)

    def scrape(self, url: str, max_pages: int, use_proxies: bool = False, rotate_proxies: bool = False) -> List[Dict[str, Any]]:
        import os
        
        books = []
        current_url = url
        current_proxy = None
        failed_queue = []
        
        # Make sure data dir exists
        os.makedirs("data", exist_ok=True)
        
        for i in range(1, max_pages + 1):
            try:
                # Use the robust fetch_page from BaseScraper
                html, current_proxy = self.fetch_page(
                    current_url, 
                    use_proxies=use_proxies, 
                    rotate_proxies=rotate_proxies, 
                    current_proxy=current_proxy
                )
                
                books.extend(self.parse_books(html, current_url))
                
                next_url = self.get_next_page_url(html, current_url)
                if not next_url:
                    break
                current_url = next_url
            except Exception as e:
                print(f"Error scraping {current_url}: {e}")
                failed_queue.append(current_url)
                
                # Log error
                with open("data/errors.txt", "a") as f:
                    f.write(f"Failed to scrape: {current_url} | Error: {e}\n")
                
                # Attempt to guess the next URL so we don't stop the whole scrape
                if "catalogue/page-" in current_url:
                    current_url = urljoin(url, f"catalogue/page-{i+1}.html")
                elif current_url == url or current_url.endswith("/"):
                    current_url = urljoin(url, "catalogue/page-2.html")
                else:
                    print("Could not guess next URL, stopping pagination.")
                    break

        # Process the failed queue at the end
        if failed_queue:
            print(f"\n--- Retrying {len(failed_queue)} failed URLs ---")
            for retry_url in failed_queue:
                try:
                    print(f"Retrying: {retry_url}")
                    html, current_proxy = self.fetch_page(
                        retry_url, 
                        use_proxies=use_proxies, 
                        rotate_proxies=rotate_proxies, 
                        current_proxy=current_proxy
                    )
                    books.extend(self.parse_books(html, retry_url))
                    print(f"Successfully scraped on retry: {retry_url}")
                except Exception as e:
                    print(f"Retry failed permanently for {retry_url}: {e}")
                    
        return books
