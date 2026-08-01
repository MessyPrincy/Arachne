from fastapi import FastAPI, HTTPException
from app.models import ScrapeRequest, ScrapeResponse
from app import scraper

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
        return ScrapeResponse(status="success", data=books)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
