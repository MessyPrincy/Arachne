from datetime import datetime
from fastapi import FastAPI, HTTPException
from app.models import ScrapeRequest, ScrapeResponse
from app import scraper
from app import exporters
from app.proxy_manager import proxy_manager

app = FastAPI(title="Arachne Scraper API")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Arachne Scraper API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/api/modules")
def list_modules():
    """List all available scraper modules."""
    return {"status": "success", "modules": scraper.get_available_modules()}

@app.post("/api/proxies/refresh")
def refresh_proxies():
    """Fetches and checks the proxy list."""
    result = proxy_manager.fetch_and_check_proxies()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@app.post("/api/scrape", response_model=ScrapeResponse)
def scrape_endpoint(request: ScrapeRequest):
    try:
        # 1. Handle Proxies
        if request.test_proxies_first:
            proxy_manager.fetch_and_check_proxies()

        if request.use_proxies and not proxy_manager.working_proxies:
            raise HTTPException(status_code=400, detail="No working proxies available. Try refreshing.")

        # 2. Select Scraper Module
        if request.module_name:
            module = scraper.get_scraper(request.module_name)
        else:
            # Fallback to books_to_scrape if none specified for backwards compatibility
            module = scraper.get_scraper("books_to_scrape")
            
        # 3. Perform the scrape
        data = module.scrape(
            request.url, 
            request.max_pages, 
            use_proxies=request.use_proxies, 
            rotate_proxies=request.rotate_proxies
        )
        
        export = request.export_format

        # No export_format, means we return the data through API
        if not export:
            return ScrapeResponse(status="success", data=data)

        if export == "db":
            filename = f"./data/scraped_data.db"
            exporters.export_to_db(data, filename, request.url)
            return ScrapeResponse(status="success")

        filename = f"./data/scraped_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{request.export_format}"

        if export == "json":
            exporters.export_to_json(data, filename)
            return ScrapeResponse(status="success")
        elif export == "csv":
            exporters.export_to_csv(data, filename)
            return ScrapeResponse(status="success")
        else:
            raise RuntimeError(f"Unsupported export format: {request.export_format}")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
