import requests
import json
import os
import random
import time
import threading
import concurrent.futures
from typing import List, Optional

PROXY_LIST_URL = "https://github.com/iplocate/free-proxy-list/raw/refs/heads/main/protocols/socks5.txt"
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
PROXIES_FILE = os.path.join(DATA_DIR, "working_proxies.json")
PROXY_TEST_URL = "http://httpbin.org/ip"
PROXY_TEST_TIMEOUT = 5

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class ProxyManager:
    def __init__(self):
        self.working_proxies: List[str] = self._load_proxies()

    def _load_proxies(self) -> List[str]:
        if os.path.exists(PROXIES_FILE):
            try:
                with open(PROXIES_FILE, "r") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading proxies from file: {e}")
        return []

    def _save_proxies(self):
        try:
            with open(PROXIES_FILE, "w") as f:
                json.dump(self.working_proxies, f)
        except Exception as e:
            print(f"Error saving proxies to file: {e}")

    def get_random_proxy(self) -> Optional[dict]:
        """Returns a proxy dictionary for requests, or None if no working proxies."""
        if not self.working_proxies:
            return None
        
        proxy_ip_port = random.choice(self.working_proxies)
        # Assuming SOCKS5 proxies
        proxy_url = f"socks5://{proxy_ip_port}"
        return {
            "http": proxy_url,
            "https": proxy_url
        }

    def fetch_and_check_proxies(self) -> dict:
        """Downloads proxy list, checks them concurrently, and saves working ones."""
        print(f"Downloading proxy list from {PROXY_LIST_URL}...")
        try:
            response = requests.get(PROXY_LIST_URL, timeout=15)
            response.raise_for_status()
            proxy_list = [line.strip() for line in response.text.split("\n") if line.strip()]
        except Exception as e:
            return {"status": "error", "message": f"Failed to download proxies: {e}"}

        print(f"Found {len(proxy_list)} proxies. Checking them...")
        
        working = []
        total_proxies = len(proxy_list)
        checked_count = 0
        lock = threading.Lock()
        
        print(f"Starting check of {total_proxies} proxies...")
        start_time = time.time()
        
        def check_proxy(proxy_str):
            nonlocal checked_count
            proxy_url = f"socks5://{proxy_str}"
            proxies = {"http": proxy_url, "https": proxy_url}
            success = False
            try:
                res = requests.get(PROXY_TEST_URL, proxies=proxies, timeout=PROXY_TEST_TIMEOUT)
                if res.status_code == 200:
                    success = True
            except Exception:
                pass
            
            with lock:
                checked_count += 1
                status_msg = "WORKING" if success else "FAILED"
                # Print progress (e.g. [15/1500])
                print(f"[{checked_count}/{total_proxies}] {proxy_str} - {status_msg}")
                
            return proxy_str if success else None

        # Check all proxies concurrently. 
        # Using 50 workers to significantly speed up the process since network requests are I/O bound.
        with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
            results = executor.map(check_proxy, proxy_list)
            for result in results:
                if result:
                    working.append(result)
                    
        self.working_proxies = working
        self._save_proxies()
        
        elapsed_time = time.time() - start_time
        print(f"\n--- PROXY CHECK COMPLETE ---")
        print(f"Checked: {total_proxies}")
        print(f"Working: {len(working)}")
        print(f"Time Taken: {elapsed_time:.2f} seconds")
        
        return {
            "status": "success",
            "message": f"Found {len(working)} working proxies out of {total_proxies} tested in {elapsed_time:.2f}s.",
            "working_count": len(working)
        }

# Global instance
proxy_manager = ProxyManager()
