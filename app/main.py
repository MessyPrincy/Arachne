from datetime import datetime
from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import RedirectResponse
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

@app.get("/scrape")
def scrape_page(request: Request):
    return templates.TemplateResponse(
        request=request, name="scrape.html"
    )

@app.post("/scrape")
def scrape_submit(url: str = Form(...), max_pages: int = Form(1), export: str = Form("db")):
    perform_scrape(url, max_pages, export or None)
    return RedirectResponse(url="/", status_code=303)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/api/scrape", response_model=ScrapeResponse)
def scrape_endpoint(request: ScrapeRequest):
    data = perform_scrape(request.url, request.max_pages, request.export_format)
    return ScrapeResponse(status="success", data=data if not request.export_format else None)


@app.get("/api/scrape-entries")
def get_scrape_entries():
    return helpers.get_chart_dict(retrievers.get_entries_per_scrapes(database))

@app.get("/api/scrape-urls")
def get_scrape_urls():
    return helpers.get_chart_dict(retrievers.get_urls_per_scrapes(database))

def perform_scrape(url: str, max_pages: int, export_format: str | None = None):
    data = scraper.scrape(url, max_pages)

    if export_format == "db":
        exporters.export_to_db(data, database, url)
    elif export_format in ("json", "csv"):
        filename = f"./data/scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format}"
        if export_format == "json":
            exporters.export_to_json(data, filename)
        else:
            exporters.export_to_csv(data, filename)
    elif export_format not in (None, ""):
        raise ValueError(f"Unsupported export format: {export_format}")

    return data
