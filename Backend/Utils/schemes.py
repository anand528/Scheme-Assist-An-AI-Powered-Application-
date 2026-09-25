# scrape_all_print.py
from typing import List, Dict, Optional, Any
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def create_driver(headless: bool = True, window_size: str = "1200,900") -> webdriver.Chrome:
    opts = Options()
    if headless:
        opts.add_argument("--headless=new")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument(f"--window-size={window_size}")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

def _normalize_whitespace(s: str) -> str:
    return " ".join((s or "").split())

def _unique_preserve_order(items):
    seen = set(); out=[]
    for x in items:
        if x not in seen:
            seen.add(x); out.append(x)
    return out

def scrape_cards_on_page(driver, wait_seconds: int = 6) -> List[Dict[str, Any]]:
    try:
        WebDriverWait(driver, wait_seconds).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']")))
    except Exception:
        time.sleep(wait_seconds)
    cards = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
    results = []
    for card in cards:
        title = ""
        ministry = ""
        desc = ""
        keywords = []
        try:
            el = card.find_element(By.CSS_SELECTOR, "h2[id^='scheme-name'] a span")
            title = el.text.strip()
        except Exception:
            try:
                el = card.find_element(By.CSS_SELECTOR, "h2")
                title = el.text.strip()
            except Exception:
                title = ""
        try:
            h2s = card.find_elements(By.TAG_NAME, "h2")
            if len(h2s) >= 2:
                ministry = h2s[1].text.strip()
            else:
                ministry = card.find_element(By.CSS_SELECTOR, "[aria-label*='Filter by Ministry']").text.strip()
        except Exception:
            ministry = ministry or ""
        try:
            desc = card.find_element(By.CSS_SELECTOR, "span[aria-label^='Brief description']").text.strip()
        except Exception:
            try:
                spans = card.find_elements(By.TAG_NAME, "span")
                if spans:
                    desc = max(spans, key=lambda s: len(s.text or "")).text.strip()
            except Exception:
                desc = ""
        try:
            tag_elements = card.find_elements(By.CSS_SELECTOR, "[role='button']")
            for t in tag_elements:
                txt = (t.text or "").strip()
                if not txt:
                    continue
                for part in txt.splitlines():
                    p = part.strip()
                    if p and 1 <= len(p) <= 80:
                        keywords.append(p)
        except Exception:
            pass

        title = _normalize_whitespace(title)
        ministry = _normalize_whitespace(ministry)
        desc = _normalize_whitespace(desc)
        keywords = _unique_preserve_order([_normalize_whitespace(k) for k in keywords])

        results.append({"scheme": title, "ministry": ministry, "description": desc, "keywords": keywords})
    return results

def _find_active_page_index(page_items):
    for idx, li in enumerate(page_items):
        cls = li.get_attribute("class") or ""
        if "bg-green-700" in cls or "bg-green-600" in cls or "bg-green" in cls or "aria-current" in li.get_attribute("outerHTML"):
            return idx
    return None

def click_next_page(driver) -> bool:
    try:
        ul = driver.find_element(By.CSS_SELECTOR, "ul.list-none")
        lis = ul.find_elements(By.XPATH, "./li")
        if not lis:
            lis = driver.find_elements(By.CSS_SELECTOR, "ul li")
        if not lis:
            return False
        active_idx = _find_active_page_index(lis)
        if active_idx is None:
            for idx, li in enumerate(lis):
                if "bg-green-700" in (li.get_attribute("innerHTML") or ""):
                    active_idx = idx
                    break
        if active_idx is not None:
            for j in range(active_idx + 1, len(lis)):
                txt = (lis[j].text or "").strip()
                if txt and txt.isdigit():
                    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", lis[j])
                    time.sleep(0.12)
                    try:
                        lis[j].click()
                        return True
                    except Exception:
                        try:
                            driver.execute_script("arguments[0].click();", lis[j])
                            return True
                        except Exception:
                            return False
    except Exception:
        pass

    # fallback: click right-arrow svg
    try:
        svgs = driver.find_elements(By.CSS_SELECTOR, "svg.cursor-pointer")
        for s in svgs:
            try:
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", s)
                time.sleep(0.1)
                s.click()
                return True
            except Exception:
                try:
                    driver.execute_script("arguments[0].click();", s)
                    return True
                except Exception:
                    continue
    except Exception:
        pass
    return False

def scrape_all_pages_and_print(headless: bool = True, max_pages: Optional[int] = 2, wait_seconds: int = 6):
    start_url = "https://www.myscheme.gov.in/search"
    driver = create_driver(headless=headless)
    all_items: List[Dict[str, Any]] = []
    try:
        driver.get(start_url)
        time.sleep(1.0)

        page_count = 0
        while True:
            page_count += 1
            items = scrape_cards_on_page(driver, wait_seconds=wait_seconds)
            if len(items)==0:
                return "Schemes Not Found"
            # deduplicate by (scheme, ministry)
            existing_keys = {(it["scheme"], it["ministry"]) for it in all_items}
            new = [it for it in items if (it["scheme"], it["ministry"]) not in existing_keys]
            all_items.extend(new)

            

            if max_pages and page_count >= max_pages:
                
                break

            clicked = click_next_page(driver)
            if not clicked:
                
                break

            # wait for load
            try:
                WebDriverWait(driver, wait_seconds).until(lambda d: d.execute_script("return document.readyState") == "complete")
            except Exception:
                time.sleep(wait_seconds * 0.5)
            time.sleep(0.6)

            # safety guard
            if page_count > 50:
                
                break

        
        return all_items

    finally:
        driver.quit()
