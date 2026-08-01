from datetime import datetime
from fastapi import FastAPI, HTTPException
from app.models import ScrapeRequest, ScrapeResponse
from app import scraper
from app import exporters

app = FastAPI(title="Arachne Scraper API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Arachne Scraper API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/scrape", response_model=ScrapeResponse)
def scrape_endpoint(request: ScrapeRequest):
    try:
        # Currently hardcoded to the bookstore logic from scraper.py
        books = scraper.scrape(request.url, request.max_pages)
        filename = f"./data/books_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.export_format}"

        match request.export_format:
            # If there is no export format, which is default, assume you export the data through the api and not save it on file
            case None:
                return ScrapeResponse(status="success", data=books)
            case "json":
                exporters.export_to_json(books, filename)
            case _:
                raise RuntimeError(f"Unsupported export format: {request.export_format}")

        return ScrapeResponse(status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
