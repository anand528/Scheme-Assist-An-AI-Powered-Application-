from backend.utils.scheme_search import WebAutomator
from backend.utils.schemes import scrape_all_pages_and_print

def list_scheme(**details) -> list:
    if details:
        automator = WebAutomator(headless=True)
        
        
        schemes = automator.open_page(**details)
        
        return schemes
    else:
        schemes=scrape_all_pages_and_print()
        return schemes




