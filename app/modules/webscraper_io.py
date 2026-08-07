from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import List, Dict, Any, Optional
from app.base_scraper import BaseScraper

class WebscraperIoScraper(BaseScraper):
    @classmethod
    def get_name(cls) -> str:
        return "webscraper_io"

    def parse_items(self, html: str, url: str) -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        cards = soup.find_all("div", class_="test-sites-card")
        items = []

        for card in cards:
            title_elem = card.find("h3", class_="card-title")
            if not title_elem:
                continue
            
            title = title_elem.get_text(strip=True)
            
            price_elem = card.find("p", class_="price")
            price = price_elem.get_text(strip=True) if price_elem else ""
            
            link_elem = title_elem.find("a")
            link = urljoin(url, link_elem.get("href", "")) if link_elem else ""
            
            items.append({"title": title, "price": price, "link": link})

        return items

    def scrape(self, url: str, max_pages: int, use_proxies: bool = False, rotate_proxies: bool = False) -> List[Dict[str, Any]]:
        items = []
        current_proxy = None
        
        for i in range(1, max_pages + 1):
            # This is where the magic happens!
            # Instead of looking for a "Next" button in the HTML, we can just 
            # simulate what the "Load More" button does under the hood by 
            # appending the page number to the URL query string!
            page_url = f"{url}?page={i}" if "?" not in url else f"{url}&page={i}"
            
            try:
                # We still get all the proxy rotation and retry logic for free!
                html, current_proxy = self.fetch_page(
                    page_url, 
                    use_proxies=use_proxies, 
                    rotate_proxies=rotate_proxies, 
                    current_proxy=current_proxy
                )
                
                new_items = self.parse_items(html, page_url)
                
                # If we loaded a page but got 0 items, we probably hit the end of the list
                if not new_items:
                    print("No more items found, stopping scrape.")
                    break
                    
                items.extend(new_items)
            except Exception as e:
                print(f"Error scraping {page_url}: {e}")
                break

        return items
