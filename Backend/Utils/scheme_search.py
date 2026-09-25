# myscheme_bot.py
from typing import List, Dict, Optional, Tuple
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# -----------------------
# Utility helpers (unchanged)
# -----------------------
def _robust_click(driver: webdriver.Chrome, element, pause=0.12) -> bool:
    """Try normal click, scroll+click, then JS click as fallback."""
    try:
        element.click()
        return True
    except Exception:
        pass
    try:
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
        time.sleep(pause)
        element.click()
        return True
    except Exception:
        pass
    try:
        driver.execute_script("arguments[0].click();", element)
        return True
    except Exception:
        return False

def _normalize_choice(v: Optional[str]) -> str:
    return (v or "").lower().strip()

def _find_label_by_text(block, target_text: str):
    """Return first label element under block whose text contains target_text (case-insensitive)."""
    try:
        labels = block.find_elements(By.TAG_NAME, "label")
        for lbl in labels:
            if target_text.lower() in (lbl.text or "").lower():
                return lbl
    except Exception:
        pass
    return None

# -----------------------
# Screen handlers (unchanged)
# -----------------------
# (place here all your existing screen1, screen2, screen3, screen4, screen5,
#  screen_income, screen_income_form, screen_government_employee implementations)
# For brevity in this listing I reuse the exact functions you already provided in your file.
# Copy the functions screen1..screen_government_employee from your original file here.
# --- BEGIN: paste existing screen functions (exactly as in your previous code) ---

# (Paste your screen1 .. screen_government_employee functions here unchanged)
# For example:
def screen1(driver, gender: str, age: int, timeout=10, status="Married"):
    wait = WebDriverWait(driver, timeout)
    gender_map = {"male": "answerMale", "female": "answerFemale", "transgender": "answerTransgender"}
    target_id = gender_map.get(_normalize_choice(gender))
    if target_id:
        lbl = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"label[for='{target_id}']")))
        if not _robust_click(driver, lbl):
            raise Exception("Could not click gender label")

    sel = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.flex select")))
    Select(sel).select_by_value(str(age))

    if _normalize_choice(gender) == "female" and int(age) >= 18:
        try:
            marital_sel = wait.until(
                EC.presence_of_element_located((
                    By.XPATH,
                    "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'marital status')]/following-sibling::div//select"
                ))
            )
            WebDriverWait(driver, timeout).until(lambda d: len(marital_sel.find_elements(By.TAG_NAME, "option")) > 1)
            Select(marital_sel).select_by_visible_text(status)
        except Exception:
            pass

    submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div/div[2]/button")))
    old = driver.current_url
    if not _robust_click(driver, submit_btn):
        raise Exception("Could not click submit on screen1")
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(old))
    except Exception:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(0.2)
    return True

def screen2(driver, state="Karnataka", residence="Urban", timeout=15):
    wait = WebDriverWait(driver, timeout)
    select_xpath = "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'please select your state')]/following-sibling::div//select"
    select_el = wait.until(EC.presence_of_element_located((By.XPATH, select_xpath)))

    def find_match():
        opts = select_el.find_elements(By.TAG_NAME, "option")
        cleaned = (state or "").strip().lower()
        for o in opts:
            if (o.text or "").strip().lower() == cleaned:
                return (o.text or "").strip()
        for o in opts:
            if cleaned in (o.text or "").strip().lower():
                return (o.text or "").strip()
        return None

    matched = WebDriverWait(driver, timeout).until(lambda d: find_match())
    if not matched:
        raise Exception(f"State '{state}' not found")
    Select(select_el).select_by_visible_text(matched)

    residence_map = {"urban": "answerUrban_residence", "rural": "answerRural_residence"}
    rid = residence_map.get(_normalize_choice(residence))
    if rid:
        lab = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, f"label[for='{rid}']")))
        _robust_click(driver, lab)

    submit_xpath = "//*[@id='__next']/div/main/div/div[2]/div/div/div/div[2]/div[2]/button"
    submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, submit_xpath)))
    old = driver.current_url
    if not _robust_click(driver, submit_btn):
        raise Exception("Could not click submit on screen2")
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(old))
    except Exception:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(0.2)
    return True

def screen3(driver, caste="Scheduled Caste (SC)", timeout=10):
    wait = WebDriverWait(driver, timeout)
    container = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'you belong to')]/following-sibling::div")))
    labels = container.find_elements(By.TAG_NAME, "label")
    cleaned_target = (caste or "").strip().lower()
    target_label = None
    for lbl in labels:
        if (lbl.text or "").strip().lower() == cleaned_target:
            target_label = lbl
            break
    if not target_label:
        for lbl in labels:
            if cleaned_target in (lbl.text or "").strip().lower():
                target_label = lbl
                break
    if target_label is None:
        raise Exception(f"Caste '{caste}' not found. Available: {[ (lbl.text or '').strip() for lbl in labels ]}")
    if not _robust_click(driver, target_label):
        raise Exception("Could not click caste label")
    submit_xpath = "//*[@id='__next']/div/main/div/div[2]/div/div/div/div[2]/div[2]/button"
    submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, submit_xpath)))
    old = driver.current_url
    if not _robust_click(driver, submit_btn):
        raise Exception("Could not click submit on screen3")
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(old))
    except Exception:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(0.2)
    return True

def screen4(driver, disability="No", percentage="30", minority="No", timeout=12):
    wait = WebDriverWait(driver, timeout)
    dis_block = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'do you identify as a person with a disability')]/following-sibling::div")))
    dis_map = {"yes": "answerYes_disability", "no": "answerNo_disability"}
    dis_id = dis_map.get(_normalize_choice(disability))
    label = None
    try:
        label = dis_block.find_element(By.CSS_SELECTOR, f"label[for='{dis_id}']")
    except Exception:
        label = _find_label_by_text(dis_block, disability)
    if label is None:
        raise Exception("Could not locate disability option label")
    if not _robust_click(driver, label):
        raise Exception("Could not click disability label")
    time.sleep(0.2)

    if _normalize_choice(disability) == "yes":
        perc_select = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'what is your differently abled percentage')]/following-sibling::div//select")))
        WebDriverWait(driver, timeout).until(lambda d: len(perc_select.find_elements(By.TAG_NAME, "option")) > 1)
        try:
            Select(perc_select).select_by_visible_text(str(percentage))
        except Exception:
            try:
                Select(perc_select).select_by_value(str(percentage))
            except Exception:
                raise Exception("Could not select percentage")
    else:
        min_block = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'do you belong to minority')]/following-sibling::div")))
        min_map = {"yes": "answerYes_minority", "no": "answerNo_minority"}
        min_id = min_map.get(_normalize_choice(minority))
        try:
            min_label = min_block.find_element(By.CSS_SELECTOR, f"label[for='{min_id}']")
        except Exception:
            min_label = _find_label_by_text(min_block, minority)
        if min_label is None or not _robust_click(driver, min_label):
            raise Exception("Could not click minority label")

    submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div/div[2]/div[2]/button")))
    old = driver.current_url
    if not _robust_click(driver, submit_btn):
        raise Exception("Could not click submit on screen4")
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(old))
    except Exception:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(0.2)
    return True

def screen5(driver, is_student="Yes", employment="Employed", is_gov_employee="No", timeout=12):
    wait = WebDriverWait(driver, timeout)
    student_block = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'are you a student')]/following-sibling::div")))
    stud_map = {"yes": "answerYes_isStudent", "no": "answerNo_isStudent"}
    sid = stud_map.get(_normalize_choice(is_student))
    try:
        stud_label = student_block.find_element(By.CSS_SELECTOR, f"label[for='{sid}']")
    except Exception:
        stud_label = _find_label_by_text(student_block, is_student)
    if stud_label is None or not _robust_click(driver, stud_label):
        raise Exception("Could not click student option")
    time.sleep(0.25)

    if _normalize_choice(is_student) == "no":
        emp_block = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'current employment status')]/following-sibling::div")))
        employment_ids = {
            "employed": "answerEmployed_employmentStatus",
            "unemployed": "answerUnemployed_employmentStatus",
            "self-employed/ entrepreneur": None
        }
        emp_id = employment_ids.get(_normalize_choice(employment))
        emp_label = None
        if emp_id:
            try:
                emp_label = emp_block.find_element(By.CSS_SELECTOR, f"label[for='{emp_id}']")
            except Exception:
                emp_label = None
        if emp_label is None:
            emp_label = _find_label_by_text(emp_block, employment)
        if emp_label is None or not _robust_click(driver, emp_label):
            raise Exception("Could not click employment option")

        time.sleep(0.25)
        gov_block = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'are you currently working as a government employee')]/following-sibling::div")))
        gov_map = {"yes": "answerYes_isGovEmployee", "no": "answerNo_isGovEmployee"}
        gid = gov_map.get(_normalize_choice(is_gov_employee))
        try:
            gov_label = gov_block.find_element(By.CSS_SELECTOR, f"label[for='{gid}']")
        except Exception:
            gov_label = _find_label_by_text(gov_block, is_gov_employee)
        if gov_label is None or not _robust_click(driver, gov_label):
            raise Exception("Could not click gov employee option")

    submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div/div[2]/div[2]/button")))
    old = driver.current_url
    if not _robust_click(driver, submit_btn):
        raise Exception("Could not click submit on screen5")
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(old))
    except Exception:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(0.2)
    return True

def screen_income(driver, is_bpl="No", timeout=12):
    wait = WebDriverWait(driver, timeout)
    bpl_block = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'do you belong to bpl category')]/following-sibling::div")))
    bpl_map = {"yes": "answerYes_isBpl", "no": "answerNo_isBpl"}
    bid = bpl_map.get(_normalize_choice(is_bpl))
    try:
        bpl_label = bpl_block.find_element(By.CSS_SELECTOR, f"label[for='{bid}']")
    except Exception:
        bpl_label = _find_label_by_text(bpl_block, is_bpl)
    if bpl_label is None or not _robust_click(driver, bpl_label):
        raise Exception("Could not click BPL option")
    time.sleep(0.18)
    submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div/div[2]/div[2]/button")))
    old = driver.current_url
    if not _robust_click(driver, submit_btn):
        raise Exception("Could not click submit on BPL screen")
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(old))
    except Exception:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(0.2)
    return True

def screen_income_form(driver, occupation, is_bpl, family_income=None, economic_distress="No", timeout=12):
    wait = WebDriverWait(driver, timeout)
    occ_select = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'is your occupation one of the following')]/following-sibling::div//select")))
    def match_option():
        opts = occ_select.find_elements(By.TAG_NAME, "option")
        cleaned = (occupation or "").strip().lower()
        for o in opts:
            if (o.text or "").strip().lower() == cleaned:
                return (o.text or "").strip()
        for o in opts:
            if cleaned in (o.text or "").strip().lower():
                return (o.text or "").strip()
        return None
    matched = WebDriverWait(driver, timeout).until(lambda d: match_option())
    if not matched:
        raise Exception(f"Occupation '{occupation}' not found")
    Select(occ_select).select_by_visible_text(matched)
    time.sleep(0.12)

    bpl_block = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'do you belong to bpl category')]/following-sibling::div")))
    bpl_map = {"yes": "answerYes_isBpl", "no": "answerNo_isBpl"}
    bid = bpl_map.get(_normalize_choice(is_bpl))
    try:
        bpl_label = bpl_block.find_element(By.CSS_SELECTOR, f"label[for='{bid}']")
    except Exception:
        bpl_label = _find_label_by_text(bpl_block, is_bpl)
    if bpl_label is None or not _robust_click(driver, bpl_label):
        raise Exception("Could not click BPL option on income form")
    time.sleep(0.15)

    if _normalize_choice(is_bpl) == "no":
        if family_income is None:
            raise ValueError("family_income required when is_bpl == 'No'")
        fam_input = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'what is your family')]/following-sibling::div//input")))
        try:
            fam_input.clear()
        except Exception:
            driver.execute_script("arguments[0].value='';", fam_input)
        fam_input.send_keys(str(family_income))
        time.sleep(0.12)
    else:
        ed_block = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'are you in any of the following condition')]/following-sibling::div")))
        ed_map = {"yes": "answerYes_isEconomicDistress", "no": "answerNo_isEconomicDistress"}
        eid = ed_map.get(_normalize_choice(economic_distress))
        try:
            ed_label = ed_block.find_element(By.CSS_SELECTOR, f"label[for='{eid}']")
        except Exception:
            ed_label = _find_label_by_text(ed_block, economic_distress)
        if ed_label is None or not _robust_click(driver, ed_label):
            raise Exception("Could not click economic distress option")

    submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div/div[2]/div[2]/button")))
    old = driver.current_url
    if not _robust_click(driver, submit_btn):
        raise Exception("Could not click submit on income form")
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(old))
    except Exception:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(0.2)
    return True

def screen_government_employee(driver, annual_income, family_income, timeout=12):
    wait = WebDriverWait(driver, timeout)
    income_input = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'what is your annual income')]/following-sibling::div//input")))
    try:
        income_input.clear()
    except Exception:
        driver.execute_script("arguments[0].value='';", income_input)
    income_input.send_keys(str(annual_income))
    time.sleep(0.12)

    family_input = wait.until(EC.presence_of_element_located((By.XPATH, "//h2[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'what is your family')]/following-sibling::div//input")))
    try:
        family_input.clear()
    except Exception:
        driver.execute_script("arguments[0].value='';", family_input)
    family_input.send_keys(str(family_income))
    time.sleep(0.12)

    submit_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//*[@id='__next']/div/main/div/div[2]/div/div/div/div[2]/div[2]/button")))
    old = driver.current_url
    if not _robust_click(driver, submit_btn):
        raise Exception("Could not click submit on government employee screen")
    try:
        WebDriverWait(driver, timeout).until(EC.url_changes(old))
    except Exception:
        WebDriverWait(driver, timeout).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(0.2)
    return True

# --- END: pasted screen functions ---

# -----------------------
# Scraper for scheme cards (unchanged)
# -----------------------
def scrape_schemes(driver, url: str, wait_seconds: int = 5) -> List[Dict[str, object]]:
    """Given a live driver and (optional) url string, scrape div[role='article'] cards.
       Note: driver should already be on the page to scrape (the url param is unused here)."""
    try:
        WebDriverWait(driver, wait_seconds).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='article']")))
    except Exception:
        time.sleep(wait_seconds)

    cards = driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
    results = []
    for card in cards:
        title_text = ""
        ministry_text = ""
        desc_text = ""
        keywords = []
        try:
            title_el = card.find_element(By.CSS_SELECTOR, "h2[id^='scheme-name'] a span")
            title_text = title_el.text.strip()
        except Exception:
            try:
                title_el = card.find_element(By.CSS_SELECTOR, "h2")
                title_text = title_el.text.strip()
            except Exception:
                title_text = ""
        try:
            h2s = card.find_elements(By.TAG_NAME, "h2")
            if len(h2s) >= 2:
                ministry_text = h2s[1].text.strip()
            else:
                ministry_el = card.find_element(By.CSS_SELECTOR, "[aria-label*='Filter by Ministry']")
                ministry_text = ministry_el.text.strip()
        except Exception:
            ministry_text = ministry_text or ""
        try:
            desc_el = card.find_element(By.CSS_SELECTOR, "span[aria-label^='Brief description']")
            desc_text = desc_el.text.strip()
        except Exception:
            try:
                spans = card.find_elements(By.TAG_NAME, "span")
                if spans:
                    longest = max(spans, key=lambda s: len(s.text or ""))
                    desc_text = longest.text.strip()
            except Exception:
                desc_text = ""
        try:
            tag_elements = card.find_elements(By.CSS_SELECTOR, "[role='button']")
            for t in tag_elements:
                txt = (t.text or "").strip()
                if txt:
                    parts = [p.strip() for p in txt.splitlines() if p.strip()]
                    if len(parts) > 1:
                        keywords.extend(parts)
                    else:
                        keywords.append(parts[0])
        except Exception:
            keywords = keywords or []

        def normalize(s: str) -> str:
            return " ".join(s.split())
        title_text = normalize(title_text)
        ministry_text = normalize(ministry_text)
        desc_text = normalize(desc_text)
        seen = set()
        normalized_keywords = []
        for k in keywords:
            nk = normalize(k)
            if nk and nk not in seen:
                seen.add(nk)
                normalized_keywords.append(nk)

        results.append({
            "scheme": title_text,
            "ministry": ministry_text,
            "description": desc_text,
            "keywords": normalized_keywords
        })
    return results

# -----------------------
# Pagination helpers (new)
# -----------------------
def _find_active_page_index(lis) -> Optional[int]:
    """Return index of the active page li (looks for class containing 'bg-green-700' or 'aria-current')."""
    for idx, li in enumerate(lis):
        cls = li.get_attribute("class") or ""
        if "bg-green-700" in cls or "bg-green-600" in cls or "bg-green" in cls or "aria-current" in li.get_attribute("outerHTML"):
            return idx
    return None

def click_next_page(driver: webdriver.Chrome) -> bool:
    """
    Try to click the next page:
      - prefer numbered pagination: find the current active <li>, click the next numeric <li>
      - fallback: click the right-arrow svg with cursor-pointer class
    Returns True if a click was performed, False otherwise.
    """
    try:
        # try to locate the pagination UL (from your markup it looks like ul.list-none)
        ul = driver.find_element(By.CSS_SELECTOR, "ul.list-none")
        lis = ul.find_elements(By.XPATH, "./li")
        if not lis:
            lis = driver.find_elements(By.CSS_SELECTOR, "ul li")
        if not lis:
            return False
        active_idx = _find_active_page_index(lis)
        if active_idx is None:
            # fallback: search for element that has the green class in innerHTML
            for idx, li in enumerate(lis):
                if "bg-green-700" in (li.get_attribute("innerHTML") or ""):
                    active_idx = idx
                    break
        if active_idx is not None:
            # click next numeric li after active
            for j in range(active_idx + 1, len(lis)):
                txt = (lis[j].text or "").strip()
                if txt and txt.isdigit():
                    try:
                        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", lis[j])
                        time.sleep(0.12)
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

    # fallback: click right-arrow svg(s)
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

# -----------------------
# Main automator (updated)
# -----------------------
class WebAutomator:
    def __init__(self, headless: bool = True):
        opts = Options()
        if headless:
            opts.add_argument("--headless=new")
        opts.add_argument("--no-sandbox")
        opts.add_argument("--disable-dev-shm-usage")
        opts.add_argument("--disable-gpu")
        opts.add_argument("--window-size=1920,1200")
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=opts)

    def open_page(self, gender: str =None, age: str =None, state: str=None, residence: str =None, caste: str =None, disability: str =None, percentage: str =None, minority: str =None, is_student: str =None, employment: str =None, is_gov_employee: str =None, is_bpl: str =None, occupation: str =None, annual_income: str =None, family_income: str =None, economic_distress: str =None, max_pages: Optional[int] = 10):
        
        """
        Navigate the flow to reach the schemes listing, then paginate and scrape all pages.
        - max_pages: optional integer limit for pages to scrape (useful for testing)
        - Other parameters: filter criteria forwarded to screen handlers
        """
        url = "https://www.myscheme.gov.in/find-scheme"
        
        try:
            self.driver.get(url)
            time.sleep(1.0)

            # go through initial screens (same as before)
            screen1(self.driver, gender=gender, age=int(age))
            time.sleep(1.0)
            screen2(self.driver, state=state, residence=residence)
            time.sleep(1.0)
            screen3(self.driver, caste=caste)
            time.sleep(1.0)
            screen4(self.driver, disability=disability, percentage=percentage, minority=minority)
            time.sleep(1.0)
            screen5(self.driver, is_student=is_student, employment=employment, is_gov_employee=is_gov_employee)
            time.sleep(1.0)

            # branch depending on student/employment
            is_student_norm = _normalize_choice(is_student)
            employment_norm = _normalize_choice(employment)

            if is_student_norm == "yes":
                screen_income(self.driver, is_bpl=is_bpl)
            else:
                if employment_norm == "unemployed":
                    screen_income(self.driver, is_bpl=is_bpl)
                elif "self" in employment_norm or "entrepreneur" in employment_norm:
                    screen_income_form(self.driver, occupation=occupation, is_bpl=is_bpl, economic_distress=economic_distress)
                elif employment_norm == "employed":
                    if _normalize_choice(is_gov_employee) == "yes":
                        screen_government_employee(self.driver, annual_income=annual_income, family_income=family_income)
                    else:
                        screen_income_form(self.driver, occupation=occupation, is_bpl=is_bpl, family_income=family_income, economic_distress=economic_distress)
                else:
                    screen_income(self.driver, is_bpl=is_bpl)

            # ensure page finish loading
            time.sleep(0.8)
            try:
                WebDriverWait(self.driver, 5).until(lambda d: d.execute_script("return document.readyState") == "complete")
            except Exception:
                pass

            # Now at listing page — paginate and scrape pages
            scraped_keys = set()  # to deduplicate by (scheme, ministry)
            page_no = 0
            while True:
                page_no += 1
                new=[]
                items = scrape_schemes(self.driver, url=None, wait_seconds=5)
                if len(items)==0:
                    return "Schemes not found"
                
                for it in items:
                    key = (it["scheme"], it["ministry"])
                    if key not in scraped_keys:
                        scraped_keys.add(key)
                        new.append(it)
                

                # apply page limit if provided
                if max_pages and page_no >= max_pages:
                    
                    break

                # attempt to click next page; stop if can't click next
                clicked = click_next_page(self.driver)
                if not clicked:
                    
                    break

                # wait for load after navigation
                try:
                    WebDriverWait(self.driver, 8).until(lambda d: d.execute_script("return document.readyState") == "complete")
                except Exception:
                    time.sleep(1.0)
                # short pause for JS to populate cards
                time.sleep(0.6)

                # safety guard
                if page_no > 50:
                    break

            
            return list(scraped_keys)

        finally:
            self.driver.quit()
