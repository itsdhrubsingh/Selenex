import json
import os
import sys
import time
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
    # Wait for navigation to {path_part}
    try:
        WebDriverWait(driver, 20).until(EC.url_contains("{path_part}"))
    except:
        print("Warning: Navigation to {path_part} timed out.")
""")
        
        self.last_url = current_url

    def _get_path(self, url):
        try:
            return urlparse(url).path
        except:
            return ""

    def _process_event(self, event):
        action = event.get("action")
        context = event.get("elementContext", {})
        tag = context.get("tag", "").upper()
        attrs = context.get("attributes", {})
        el_type = attrs.get("type", "").lower() if attrs.get("type") else ""
        
        if action == "click":
            strategy, value = self.selector_engine.get_best_selector(event)
            return f"""
    # Click {value}
    try:
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(({strategy}, "{value}"))
        )
        driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", element)
        
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable(({strategy}, "{value}")))
            ActionChains(driver).move_to_element(element).click().perform()
        except:
            driver.execute_script("arguments[0].click();", element)
            
    except Exception as e:
        print(f"Error clicking {value}: {{e}}")
"""

        elif action == "input":
            val = event.get("value", "")
            strategy, locator = self.selector_engine.get_best_selector(event)
            
            # Select/Dropdown
            if tag == "SELECT":
                 return f"""
    # Select '{val}' in {locator}
    try:
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(({strategy}, "{locator}"))
        )
        driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", element)
        try:
            Select(element).select_by_value("{val}")
        except:
            Select(element).select_by_visible_text("{val}")
    except Exception as e:
        print(f"Error selecting {val} in {locator}: {{e}}")
"""

            # Radio/Checkbox
            if el_type in ["radio", "checkbox"]:
                return f"    # Skipped input for {el_type} (handled by click)"

            # Standard Text Input
            return f"""
    # Type '{val}' into {locator}
    try:
        element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located(({strategy}, "{locator}"))
        )
        driver.execute_script("arguments[0].scrollIntoView({{block: 'center'}});", element)
        element.clear()
        element.send_keys("{val}")
    except Exception as e:
        print(f"Error inputting text {locator}: {{e}}")
"""

        elif action == "scroll":
            x = event.get("x", 0)
            y = event.get("y", 0)
            if x == 0 and y == 0:
                return f"    # Skipped scroll(0,0)"
            return f"""
    driver.execute_script('window.scrollTo({x}, {y})')
"""

        elif action == "keydown":
            key = event.get("key")
            selenium_key = self._map_key(key)
            if not selenium_key: return f"    # Unsupported key: {key}"
            
            return f"""
    try:
        ActionChains(driver).send_keys(Keys.{selenium_key}).perform()
    except:
        driver.switch_to.active_element.send_keys(Keys.{selenium_key})
"""

        return f"    # Unknown action: {action}"

    def _map_key(self, key):
        key_map = {
            "Enter": "ENTER",
            "Tab": "TAB",
            "Escape": "ESCAPE"
        }
        return key_map.get(key)

    def _generate_header(self, start_url):
        return f"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

def run_test():
    print("Starting Test...")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)
    
    driver.get("{start_url}")
"""

    def _generate_footer(self):
        return """
    print("Test Completed Successfully")
    time.sleep(2)
    driver.quit()

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
"""
