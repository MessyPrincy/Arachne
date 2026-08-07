import os
import importlib
import inspect
from typing import Dict, Type
from app.base_scraper import BaseScraper

# Dictionary to hold the loaded scraper classes
_SCRAPER_REGISTRY: Dict[str, Type[BaseScraper]] = {}

def load_modules():
    """Dynamically loads all scraper modules from the app/modules directory."""
    global _SCRAPER_REGISTRY
    _SCRAPER_REGISTRY.clear()
    
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    
    for filename in os.listdir(modules_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            module_name = filename[:-3]
            try:
                # Import the module
                module = importlib.import_module(f"app.modules.{module_name}")
                
                # Find classes in the module that inherit from BaseScraper
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseScraper) and obj is not BaseScraper:
                        scraper_name = obj.get_name()
                        _SCRAPER_REGISTRY[scraper_name] = obj
                        print(f"Loaded scraper module: {scraper_name}")
            except Exception as e:
                print(f"Error loading module {module_name}: {e}")

# Load modules on startup
load_modules()

def get_available_modules() -> list[str]:
    """Returns a list of available scraper module names."""
    return list(_SCRAPER_REGISTRY.keys())

def get_scraper(module_name: str) -> BaseScraper:
    """Returns an instance of the requested scraper module."""
    scraper_class = _SCRAPER_REGISTRY.get(module_name)
    if not scraper_class:
        raise ValueError(f"Scraper module '{module_name}' not found.")
    return scraper_class()
