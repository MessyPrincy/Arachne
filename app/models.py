from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ScrapeRequest(BaseModel):
    url: str
    use_ai: bool = False
    max_pages: Optional[int] = 1

class ScrapeResponse(BaseModel):
    status: str
    data: List[Dict[str, Any]]
