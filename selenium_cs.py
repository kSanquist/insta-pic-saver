from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent


def load_ua():
    """Loads fake user agent (I think it helps avoid auto-ban?)"""
    ua = UserAgent()
    user_agent = ua.random
    print(user_agent)


def start_webdriver(url: str, headless=True) -> webdriver:
    """Starts webdriver w/ optional arguments and returns it"""
    options = Options()
    options.add_experimental_option('detach', True)
    options.add_argument("--headless=new") if headless else ""
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)
    driver.get(url)
    return driver


# By: XPATH, NAME, CSS_SELECTOR, CLASS_NAME
def get_elem(driver: webdriver, by: By, value: str):
    """Used for getting webpage elements"""
    element = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((by, value)))
    return element


def get_elems(driver: webdriver, by: By, value: str):
    elements = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((by, value)))
    return elements


def new_tab(driver: webdriver, url: str):
    """Creates a new tab"""
    driver.execute_script("window.open('');")
    handle_idx = len(driver.window_handles) - 1
    driver.switch_to.window(driver.window_handles[handle_idx])
    driver.get(url)
