"""Web scraper module"""

import json
import re

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

ROOT_URL = "https://publicauctionreno.hibid.com/"

CATEGORY_ID: str = "auction-search-group"
DISMISS_BUTTON_CLASS: str = "btn btn-secondary ng-star-inserted"
LOT_CLASS: str = (
    "lot-number-lead lot-link lot-title-ellipsis lot-preview-link link mb-1 ng-star-inserted"
)
SEARCH_XPATH: str = (
    "/html/body/app-root/div[1]/main/div/div/app-catalog/div/div[1]/app-auction-search-private/div/div[1]/div/input"
)

TOP_LEVEL_CATEGORIES: list[str] = [
    "All Categories",
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

JOB_DICT = {
    "keywords": [
        "chair",
        "chromebook",
    ],
    "categories": [
        TOP_LEVEL_CATEGORIES[4],
        TOP_LEVEL_CATEGORIES[3],
    ],
}


def dismiss_popup(driver: webdriver) -> None:
    """Clicks popup to dismiss"""
    button_element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, f"button[class='{DISMISS_BUTTON_CLASS}']")
        )
    )
    button_element.click()


def navigate_to_auction_page(driver: webdriver) -> None:
    """Redirects driver to auction main page from home page"""
    driver.get(ROOT_URL)
    driver.implicitly_wait(2)
    button_element = driver.find_element(
        By.XPATH, '//*[@id="auction-ststus-badges"]/app-auction-status/div[1]/a'
    )
    try:
        button_element.click()
    except ElementClickInterceptedException:
        dismiss_popup(driver)
        button_element.click()


def navigate_by_search_term(driver: webdriver, search_term: str) -> None:
    """Redirects driver to keyword results page"""
    driver.implicitly_wait(5)
    input_element = driver.find_element(By.XPATH, SEARCH_XPATH)
    input_element.clear()
    input_element.send_keys(search_term)
    input_element.send_keys(Keys.ENTER)


def navigate_by_category(driver: webdriver, category: str) -> None:
    """Redirects driver to category page"""
    select_element = driver.find_element(By.ID, CATEGORY_ID)
    select: Select = Select(select_element)
    category_index = get_dropdown_index(select.options, category)
    select.select_by_value(f"{category_index}: Object")
    # select.select_by_index(category_index)


def get_dropdown_index(dropdown_options: list, category: str) -> int:
    """Returns index of first category match"""
    # TODO clean string parse implementation
    # remove ' (count)' pattern
    top_level_dropdown_options = [
        re.sub(r"\d", "", option.text.replace(" (", "").replace(")", ""))
        for option in dropdown_options
    ]  # try element.text for matching
    return top_level_dropdown_options.index(category)


def create_driver() -> webdriver:
    """Creates web driver"""
    driver_options = Options()
    driver_options.add_argument("--headlness=new")
    driver = webdriver.Firefox(options=driver_options)
    return driver


def get_page_listings(driver: webdriver) -> dict:
    """Returns list of auction listings"""
    driver.get(driver.current_url)
    driver.implicitly_wait(5)
    lots_dict = {}
    lots = driver.find_elements(By.CSS_SELECTOR, f"a[class='{LOT_CLASS}']")
    for lot_element in lots:
        lot_name = get_listing_name(lot_element)
        lot_link = get_listing_link(lot_element)
        if lot_name in lots_dict:
            lots_dict[lot_name].append(lot_link)
        else:
            lots_dict[lot_name] = [lot_link]
    return lots_dict


def get_listing_link(listing_element) -> str:
    """Retrieves href value from anchor element"""
    return listing_element.get_attribute("href")


def get_listing_name(listing_element) -> str:  # webelement
    """Extracts listing name from parent element"""
    header_element = listing_element.find_element(By.XPATH, "h2")
    lot_title: str = header_element.get_attribute("innerHTML")
    return lot_title


def export_listings(listing_details: dict, fname: str = "lot_details.json") -> None:
    """Exports listings details to JSON file"""
    with open(fname, "w", encoding="utf-8") as json_file:
        json.dump(listing_details, json_file, indent=4)


def get_keyword_listings(driver: webdriver, keywords: list[str]) -> dict:
    """Gets all listings by keyword"""
    keyword_listings: dict[dict] = {}
    for keyword in keywords:
        try:
            navigate_by_search_term(driver, keyword)
        except ElementClickInterceptedException:
            dismiss_popup(driver)
            navigate_by_search_term(driver, keyword)
        driver.implicitly_wait(5)
        keyword_listings[keyword] = get_page_listings(driver)
    return keyword_listings


def get_categoric_listings(driver: webdriver, categories: list[str]) -> dict:
    """Gets all listings by category"""
    categoric_listings: dict[dict] = {}
    for category in categories:
        try:
            navigate_by_category(driver, category)
        except ElementClickInterceptedException:
            dismiss_popup(driver)
            navigate_by_category(driver, category)
        driver.implicitly_wait(5)
        categoric_listings[category] = get_page_listings(driver)
    return categoric_listings


def get_listings_by_job(
    driver: webdriver, job_config: dict[str, list[str]]
) -> dict[str, dict[str, list[str]]]:
    """Gets all listings by configuration in the job"""
    all_listings: dict = {}
    navigate_to_auction_page(driver)
    all_listings |= get_categoric_listings(driver, job_config["categories"])
    navigate_to_auction_page(driver)
    all_listings |= get_keyword_listings(driver, job_config["keywords"])
    return all_listings


def main():
    """Runs web session"""
    driver = create_driver()
    lot_details: dict = get_listings_by_job(driver, JOB_DICT)
    driver.quit()
    export_listings(lot_details)


if __name__ == "__main__":
    main()
