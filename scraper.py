"""Web scraper module"""

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

ROOT_URL = 'https://publicauctionreno.hibid.com/'

def navigate_to_auction_page(driver: webdriver) -> None:
    """Redirects driver to auction main page from home page"""
    driver.get(ROOT_URL)
    driver.implicitly_wait(2)
    button_element = driver.find_element(
        By.XPATH, '//*[@id="auction-ststus-badges"]/app-auction-status/div[1]/a'
    )
    button_element.click()

def navigate_by_search_term(driver: webdriver, search_term: str) -> None:
    """Redirects drivers to keyword results page"""
    driver.implicitly_wait(2)
    search_xpath = '/html/body/app-root/div[1]/main/div/div/app-catalog/div/div[1]/app-auction-search-private/div/div[1]/div/input'
    input_element = driver.find_element(By.XPATH, search_xpath)
    input_element.send_keys(search_term)
    input_element.send_keys(Keys.ENTER)

def create_driver() -> webdriver:
    """Creates web driver"""
    driver_options = Options()
    driver_options.add_argument("--headlness=new")
    driver = webdriver.Firefox(options=driver_options)
    return driver

def main():
    """Runs web session"""
    driver = create_driver()
    driver.get(ROOT_URL)
    navigate_to_auction_page(driver)
    navigate_by_search_term(driver, "chair")
    driver.quit()

if __name__ == "__main__":
    main()
