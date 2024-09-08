"""Web scraper module"""

import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select

ROOT_URL = "https://publicauctionreno.hibid.com/"

TOP_LEVEL_CATEGORIES = [
    "Antiques & Collectables",
    "Business & Industrial",
    "Cars & Vehicles",
    "Computers & Electronics",
    "Construction & Farm",
    "Fashion",
    "Furniture",
    "Home Good & Decor",
    "Kid & Baby Essentials",
    "Lawn & Garden",
    "Sporting Goods",
    "Toys",
]


def navigate_to_auction_page(driver: webdriver) -> None:
    """Redirects driver to auction main page from home page"""
    driver.get(ROOT_URL)
    driver.implicitly_wait(2)
    button_element = driver.find_element(
        By.XPATH, '//*[@id="auction-ststus-badges"]/app-auction-status/div[1]/a'
    )
    button_element.click()


def navigate_by_search_term(driver: webdriver, search_term: str) -> None:
    """Redirects driver to keyword results page"""
    driver.implicitly_wait(2)
    search_xpath: str = (
        "/html/body/app-root/div[1]/main/div/div/app-catalog/div/div[1]/app-auction-search-private/div/div[1]/div/input"
    )
    input_element = driver.find_element(By.XPATH, search_xpath)
    input_element.send_keys(search_term)
    input_element.send_keys(Keys.ENTER)


def navigate_by_category(driver: webdriver, category: str) -> None:
    """Redirects driver to category page"""
    category_id: str = "auction-search-group"
    select_element = driver.find_element(By.ID, category_id)
    select: Select = Select(select_element)
    category_index = get_dropdown_index(select.options, category)
    select.select_by_index(category_index)


def get_dropdown_index(dropdown_options: list, category: str) -> int:
    """Returns index of first category match"""
    # TODO clean string parse implementation
    # remove ' (count)' pattern
    top_level_dropdown_options = [
        re.sub(r"\d", "", option.replace(" (", "").replace( ")", ""))
        for option in dropdown_options
    ]
    print(top_level_dropdown_options)
    return top_level_dropdown_options.index(category)


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
