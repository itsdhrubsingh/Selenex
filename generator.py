import json
import os
import sys
from selenium.webdriver.common.by import By
from urllib.parse import urlparse

class SelectorEngine:
    """
    Heuristic-based Selector Engine.
    """
    def __init__(self):
        pass

    def get_best_selector(self, event):
        context = event.get("elementContext", {})
        
        tag = context.get("tag", "").upper()
        text = context.get("text", "")
        attributes = context.get("attributes", {})
        
        el_id = attributes.get("id")
        name = attributes.get("name")
        href = attributes.get("href")
        data_testid = attributes.get("dataTestId")
        placeholder = attributes.get("placeholder")
        classes = attributes.get("class", "")
        
        parents = context.get("parentChain", [])

        # 1. Golden: Data Attribute
        if data_testid:
            return "By.CSS_SELECTOR", f"[{data_testid}]" if "=" in data_testid else f"[data-testid='{data_testid}']"

        # 2. Golden: Stable ID
        if el_id and not self._is_dynamic_id(el_id):
            return "By.ID", el_id

        # 3. Silver: Input Name
        if tag in ["INPUT", "SELECT", "TEXTAREA"] and name:
            return "By.NAME", name

        # 4. Silver: Href
        if tag == "A" and href and href.startswith("/"):
            return "By.XPATH", f"//a[@href='{href}']"
        
        # 5. Silver: Semantic Text
        if text and len(text) < 50:
            clean_text = text.replace("'", "\\'")
            if tag == "A":
                return "By.LINK_TEXT", text
            if tag == "BUTTON":
                return "By.XPATH", f"//button[normalize-space()='{clean_text}']"
            if tag in ["SPAN", "DIV", "P", "H1", "H2", "H3", "H4", "H5", "H6"]:
                return "By.XPATH", f"//{tag.lower()}[normalize-space()='{clean_text}']"

        # 6. Bronze: Parent Chain Heuristics
        if parents:
            for parent in parents:
                p_id = parent.get("id")
                p_tag = parent.get("tag", "").lower()
                if p_id and not self._is_dynamic_id(p_id):
                    return "By.XPATH", f"//{p_tag}[@id='{p_id}']//{tag.lower()}"
        
        # 7. Fallback: Classes
        if classes:
            meaningful_classes = [c for c in classes.split() if not c.startswith("wds-") and not c.startswith("hover:")]
            if meaningful_classes:
               class_selector = "." + ".".join(meaningful_classes)
               return "By.CSS_SELECTOR", f"{tag.lower()}{class_selector}"

        if placeholder:
             return "By.XPATH", f"//{tag.lower()}[@placeholder='{placeholder}']"

        return "By.CSS_SELECTOR", f"{tag.lower()}"

    def _is_dynamic_id(self, el_id):
        if not el_id: return False
        if "vid-" in el_id or "prj-" in el_id: return False
        if any(char.isdigit() for char in el_id) and len(el_id) > 10:
            return True
        return False

class CodeGenerator:
    def __init__(self, output_file="test_script.py"):
        self.output_file = output_file
        self.selector_engine = SelectorEngine()
        self.steps = []
        self.last_url = None

    def load_session(self, session_path):
        with open(session_path, 'r') as f:
            self.events = json.load(f)

    def generate(self):
        start_url = "https://google.com"
        if self.events:
            for e in self.events:
                fp = e.get("fingerprint", {})
                if "url" in fp:
                    start_url = fp["url"]
                    break
        
        self.last_url = start_url
        
        header = self._generate_header(start_url)
        
        for event in self.events:
            self._handle_navigation(event)
            step_code = self._process_event(event)
            if step_code:
                self.steps.append(step_code)
        
        footer = self._generate_footer()
        full_script = header + "\n" + "\n".join(self.steps) + "\n" + footer
        
        with open(self.output_file, "w") as f:
            f.write(full_script)
        
        return self.output_file

    def _handle_navigation(self, event):
        """Intersects URL changes to add explicit waits."""
        current_url = event.get("fingerprint", {}).get("url")
        if not current_url or not self.last_url:
            return

        if self._get_path(current_url) != self._get_path(self.last_url):
            path_part = self._get_path(current_url).strip("/")
            if "/" in path_part: path_part = path_part.split("/")[0]
            
            if path_part:
                self.steps.append(f"""
    # Detected URL change to {path_part}
    logger.info("Waiting for navigation to {path_part}...")
    try:
        WebDriverWait(driver, 15).until(EC.url_contains("{path_part}"))
        logger.info("Navigation check passed.")
    except:
        logger.warning("Navigation timeout - verify if URL is correct.")
""")
        
        self.last_url = current_url

    def _get_path(self, url):
        try:
            return urlparse(url).path
        except:
            return ""

    def _generate_header(self, start_url):
        return f"""
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("automation.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

def run_test():
    logger.info("Starting Automation Script")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    
    logger.info("Navigating to start URL: {start_url}")
    driver.get("{start_url}")
"""

    def _process_event(self, event):
        action = event.get("action")
        timestamp = event.get("timestamp")
        context = event.get("elementContext", {})
        tag = context.get("tag", "").upper()
        attrs = context.get("attributes", {})
        el_type = attrs.get("type", "").lower() if attrs.get("type") else ""
        
        if action == "click":
            strategy, value = self.selector_engine.get_best_selector(event)
            return f"""
    try:
        logger.info("Clicking element: {value}")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(({strategy}, "{value}"))
        )
        # 1. Scroll into view (JS)
        driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", element)
        time.sleep(0.5)
        
        # 2. Try ActionChains (Robust Mouse Move + Click)
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(({strategy}, "{value}")))
            ActionChains(driver).move_to_element(element).click().perform()
        except:
            logger.warning("Standard click failed, attempting JS Force Click.")
            driver.execute_script("arguments[0].click();", element)
            
    except Exception as e:
        logger.error(f"Failed to click {value}: {{e}}")
"""

        elif action == "input":
            # Smart handling based on element type
            val = event.get("value", "")
            strategy, locator = self.selector_engine.get_best_selector(event)
            
            # Case 1: Select/Dropdown
            if tag == "SELECT":
                 return f"""
    logger.info("Selecting value '{{val}}' in dropdown: {locator}")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(({strategy}, "{locator}"))
        )
        driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", element)
        Select(element).select_by_value("{val}") # Try value first
    except:
        try:
            Select(element).select_by_visible_text("{val}") # Fallback to text
        except Exception as e:
            logger.error(f"Failed to select {val} in {locator}: {{e}}")
"""

            # Case 2: Radio or Checkbox
            # user 'input' event on these means "value changed", but the click usually handles the interaction.
            # Sending keys to a radio button is invalid.
            if el_type in ["radio", "checkbox"]:
                return f"    # Skipping 'input' action for {el_type} (handled by click)"

            # Case 3: Standard Text Input
            return f"""
    logger.info("Inputting text into: {locator}")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(({strategy}, "{locator}"))
        )
        driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", element)
        time.sleep(0.2)
        element.clear()
        element.send_keys("{val}")
    except Exception as e:
        logger.error(f"Failed to input text {locator}: {{e}}")
"""

        elif action == "scroll":
            x = event.get("x", 0)
            y = event.get("y", 0)
            if x == 0 and y == 0:
                return f"    # Skipping captured scroll (0,0)"
            return f"""
    logger.info("Scrolling to ({x}, {y})")
    driver.execute_script('window.scrollTo({x}, {y})')
"""

        elif action == "keydown":
            key = event.get("key")
            selenium_key = self._map_key(key)
            if not selenium_key: return f"    # Unsupported key: {key}"
            
            return f"""
    logger.info("Sending Key: {key}")
    try:
        ActionChains(driver).send_keys(Keys.{selenium_key}).perform()
    except:
        driver.switch_to.active_element.send_keys(Keys.{selenium_key})
"""

        return f"    # Unknown action: {action}"

    def _generate_footer(self):
        return """
    logger.info("Test Completed Successfully")
    time.sleep(2)
    driver.quit()

if __name__ == "__main__":
    run_test()
"""

if __name__ == "__main__":
    if len(sys.argv) > 1:
        session_path = sys.argv[1]
    else:
        session_path = "session.json"
    
    if os.path.exists(session_path):
        print(f"Generating script from {session_path}...")
        gen = CodeGenerator()
        gen.load_session(session_path)
        out = gen.generate()
        print(f"Generated test script: {out}")
    else:
        print("session.json not found.")
