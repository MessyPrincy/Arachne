# Arachne Scraper API

A web scraper API built with FastAPI and BeautifulSoup.

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
uvicorn app.main:app --reload --port 8000
```

## Usage

### Interactive Docs
When the server is running, visit `http://localhost:8000/docs` to use the built-in Swagger UI.

### Endpoints

**`GET /health`**
Check if the API is running.
```bash
curl http://localhost:8000/health
```

**`POST /api/scrape`**
Scrape a target website. (Currently hardcoded for `books.toscrape.com`).

*Request body parameters:*
- `url` (string, required)
- `max_pages` (int, optional, default: 1)
- `use_ai` (bool, optional, default: false)
- `export_format` (string (json, csv, db), optional, default: None)

*Example:*
```bash
curl -X POST http://localhost:8000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"url": "http://books.toscrape.com/", "max_pages": 1, "export_format": "db"}'
```
