import requests
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from app.proxy_manager import proxy_manager

class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, url: str, max_pages: int, use_proxies: bool = False, rotate_proxies: bool = False) -> List[Dict[str, Any]]:
        """
        Main entry point for scraping.
        Must return a list of dictionaries containing the scraped data.
        """
        pass

    @classmethod
    @abstractmethod
    def get_name(cls) -> str:
        """
        Returns the unique identifier/name for this scraper module.
        """
        pass

    def fetch_page(self, url: str, use_proxies: bool, rotate_proxies: bool, current_proxy: Optional[dict], max_retries: int = 3) -> tuple[str, Optional[dict]]:
        """
        Robustly fetches a page, automatically handling proxy rotation and retries.
        Returns the HTML content and the proxy dictionary that was ultimately successful.
        """
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        retries = 0
        proxy = current_proxy

        while retries <= max_retries:
            # Decide if we need a new proxy for this request
            if use_proxies and (rotate_proxies or proxy is None):
                proxy = proxy_manager.get_random_proxy()
                if not proxy and use_proxies:
                    # If we really want proxies but none are available
                    raise Exception("No working proxies available in the pool.")
            
            try:
                print(f"Fetching {url} with proxy {proxy} (Attempt {retries+1}/{max_retries+1})")
                response = requests.get(url, proxies=proxy, headers=headers, timeout=10)
                response.raise_for_status()
                return response.text, proxy
            except Exception as e:
                print(f"Request failed: {e}")
                retries += 1
                if use_proxies:
                    print("Retrying with a new proxy...")
                    proxy = None # Force a new proxy on the next iteration
                else:
                    print("Retrying...")
        
        raise Exception(f"Failed to fetch {url} after {max_retries} retries.")
