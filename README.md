# Arachne Scraper API

A modular, highly resilient web scraper API built with FastAPI and BeautifulSoup.

## What's New

Arachne is no longer a simple hardcoded script. It's now a fully modular framework with a built-in proxy manager.
- **Drop-in Modules**: Add new scrapers simply by creating a python file in the `app/modules/` directory.
- **Auto Proxy Fetching**: Pulls and verifies free SOCKS5 proxies on the fly.
- **Bulletproof Retries**: Network hiccup? Proxy banned? The scraper automatically drops dead proxies, grabs fresh ones, and retries the page.
- **Failed URL Queue**: If a page truly fails after multiple retries, it's queued up and retried at the very end of the scrape. Failed pages are also logged to `data/errors.txt` so you never lose track.

## Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Server

Start the API from the project root directory:
```bash
venv/bin/uvicorn app.main:app --reload --port 8000
```

## Usage

### Interactive Docs
When the server is running, visit `http://localhost:8000/docs` to use the built-in Swagger UI and test endpoints directly from your browser.

### Endpoints

**`GET /health`**
Check if the API is running.

**`GET /api/modules`**
Returns a list of all detected scraper modules you can use.

**`POST /api/proxies/refresh`**
Forces the proxy manager to download a fresh list of proxies and test them concurrently to find working ones.

**`POST /api/scrape`**
Trigger a scrape.

*Parameters:*
- `url` (string, required): The starting URL.
- `max_pages` (int, optional, default: 1): How many pages to scrape.
- `module_name` (string, optional): Which scraper module to use (e.g., `books_to_scrape`).
- `use_proxies` (bool, optional, default: false): Toggle whether to route traffic through SOCKS5 proxies.
- `rotate_proxies` (bool, optional, default: false): If true, it uses a brand new proxy for every single page request. If false, it tries to stick with one proxy (but will swap if it dies).
- `test_proxies_first` (bool, optional, default: false): Forces a proxy list refresh right before the scrape starts.
- `export_format` (string, optional): Can be `json`, `csv`, or `db`. If left empty, returns data directly in the API response.

*Example - Heavy Duty Scrape:*
```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "url": "http://books.toscrape.com/",
    "max_pages": 5,
    "module_name": "books_to_scrape",
    "use_proxies": true,
    "rotate_proxies": true
  }'
```

## Creating New Modules

Adding a new target is easy:
1. Create a new `.py` file inside `app/modules/`.
2. Create a class that inherits from `BaseScraper`.
3. Implement the `get_name()` and `scrape()` methods.
4. Call `self.fetch_page()` whenever you need to download HTML. It automatically handles all the proxy rotation, retries, and error logging for you under the hood!
