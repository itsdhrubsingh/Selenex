
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
    
    logger.info("Navigating to start URL: https://rahulshettyacademy.com/AutomationPractice/")
    driver.get("https://rahulshettyacademy.com/AutomationPractice/")


    try:
        logger.info("Clicking element: radioButton")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "radioButton"))
        )
        # 1. Scroll into view (JS)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        
        # 2. Try ActionChains (Robust Mouse Move + Click)
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "radioButton")))
            ActionChains(driver).move_to_element(element).click().perform()
        except:
            logger.warning("Standard click failed, attempting JS Force Click.")
            driver.execute_script("arguments[0].click();", element)
            
    except Exception as e:
        logger.error(f"Failed to click radioButton: {e}")

    # Skipping 'input' action for radio (handled by click)

    try:
        logger.info("Clicking element: autocomplete")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "autocomplete"))
        )
        # 1. Scroll into view (JS)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        
        # 2. Try ActionChains (Robust Mouse Move + Click)
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "autocomplete")))
            ActionChains(driver).move_to_element(element).click().perform()
        except:
            logger.warning("Standard click failed, attempting JS Force Click.")
            driver.execute_script("arguments[0].click();", element)
            
    except Exception as e:
        logger.error(f"Failed to click autocomplete: {e}")


    logger.info("Inputting text into: autocomplete")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "autocomplete"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.2)
        element.clear()
        element.send_keys("United Arab Emirates")
    except Exception as e:
        logger.error(f"Failed to input text autocomplete: {e}")


    try:
        logger.info("Clicking element: dropdown-class-example")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dropdown-class-example"))
        )
        # 1. Scroll into view (JS)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        
        # 2. Try ActionChains (Robust Mouse Move + Click)
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "dropdown-class-example")))
            ActionChains(driver).move_to_element(element).click().perform()
        except:
            logger.warning("Standard click failed, attempting JS Force Click.")
            driver.execute_script("arguments[0].click();", element)
            
    except Exception as e:
        logger.error(f"Failed to click dropdown-class-example: {e}")


    logger.info("Selecting value '{val}' in dropdown: dropdown-class-example")
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dropdown-class-example"))
        )
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        Select(element).select_by_value("option2") # Try value first
    except:
        try:
            Select(element).select_by_visible_text("option2") # Fallback to text
        except Exception as e:
            logger.error(f"Failed to select option2 in dropdown-class-example: {e}")


    try:
        logger.info("Clicking element: dropdown-class-example")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dropdown-class-example"))
        )
        # 1. Scroll into view (JS)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        
        # 2. Try ActionChains (Robust Mouse Move + Click)
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.ID, "dropdown-class-example")))
            ActionChains(driver).move_to_element(element).click().perform()
        except:
            logger.warning("Standard click failed, attempting JS Force Click.")
            driver.execute_script("arguments[0].click();", element)
            
    except Exception as e:
        logger.error(f"Failed to click dropdown-class-example: {e}")


    try:
        logger.info("Clicking element: checkBoxOption3")
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "checkBoxOption3"))
        )
        # 1. Scroll into view (JS)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(0.5)
        
        # 2. Try ActionChains (Robust Mouse Move + Click)
        try:
            WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.NAME, "checkBoxOption3")))
            ActionChains(driver).move_to_element(element).click().perform()
        except:
            logger.warning("Standard click failed, attempting JS Force Click.")
            driver.execute_script("arguments[0].click();", element)
            
    except Exception as e:
        logger.error(f"Failed to click checkBoxOption3: {e}")

    # Skipping 'input' action for checkbox (handled by click)

    logger.info("Test Completed Successfully")
    time.sleep(2)
    driver.quit()

if __name__ == "__main__":
    run_test()
