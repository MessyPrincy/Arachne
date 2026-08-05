from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.models import ScrapeRequest, ScrapeResponse
from app import scraper, exporters, retrievers, helpers

app = FastAPI(title="Arachne Scraper API")
templates = Jinja2Templates(directory="templates")
database = "./data/scraped_data.db"

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html"
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/scrape", response_model=ScrapeResponse)
def scrape_endpoint(request: ScrapeRequest):
    try:
        # Currently hardcoded to the bookstore logic from scraper.py
        data = scraper.scrape(request.url, request.max_pages)
        export = request.export_format
        filename = f"./data/scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.export_format}"

        # No export_format, means we return the data through API
        if not export:
            return ScrapeResponse(status="success", data=data)
        elif export == "db":
            exporters.export_to_db(data, database, request.url)
        elif export == "json":
            exporters.export_to_json(data, filename)
        elif export == "csv":
            exporters.export_to_csv(data, filename)
        # This is important, never trust user input    
        else:
            raise ValueError(f"Unsupported export format: {request.export_format}")
        return ScrapeResponse(status="success")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/scrape-entries")
def get_scrape_entries():
    return helpers.get_chart_dict(retrievers.get_entries_per_scrapes(database))

@app.get("/api/scrape-urls")
def get_scrape_urls():
    return helpers.get_chart_dict(retrievers.get_urls_per_scrapes(database))
