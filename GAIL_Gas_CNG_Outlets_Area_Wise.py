import time
import re
import os
import pandas as pd

from urllib.parse import unquote

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import (
    TimeoutException,
    StaleElementReferenceException,
    ElementClickInterceptedException
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_URL = "https://gailgas.com/"

OUTPUT_FOLDER = "GAIL_Gas_CNG_Outlets_Area_Wise"

WAIT = 20

PAGE_DELAY = 1.5


# ============================================================
# CREATE CHROME DRIVER
# ============================================================

def create_driver():

    options = Options()

    # Keep Chrome visible while testing.
    # After confirming everything works, uncomment:
    #
    # options.add_argument("--headless=new")

    options.add_argument("--start-maximized")

    options.add_argument(
        "--disable-notifications"
    )

    options.add_argument(
        "--disable-popup-blocking"
    )

    options.add_argument(
        "--disable-blink-features=AutomationControlled"
    )

    options.add_argument(
        "--no-sandbox"
    )

    options.add_argument(
        "--disable-dev-shm-usage"
    )

    options.add_experimental_option(
        "excludeSwitches",
        ["enable-automation"]
    )

    options.add_experimental_option(
        "useAutomationExtension",
        False
    )

    driver = webdriver.Chrome(
        options=options
    )

    driver.set_page_load_timeout(
        60
    )

    return driver


# ============================================================
# CLEAN TEXT
# ============================================================

def clean_text(text):

    if text is None:
        return ""

    text = str(text)

    text = text.replace(
        "\xa0",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CLOSE GAIL POPUP
# ============================================================

def close_popup(driver):

    """
    Exact GAIL popup close element:

    <svg
        mat-dialog-close=""
        id="txtt"
        class="bi bi-x-circle"
    >

    Selector:
        svg#txtt[mat-dialog-close]
    """

    try:

        elements = driver.find_elements(
            By.CSS_SELECTOR,
            "svg#txtt[mat-dialog-close]"
        )

        for element in elements:

            try:

                if not element.is_displayed():
                    continue

                print(
                    "Popup detected - closing..."
                )

                driver.execute_script(
                    """
                    arguments[0].scrollIntoView({
                        block: 'center',
                        inline: 'center'
                    });
                    """,
                    element
                )

                time.sleep(
                    0.3
                )

                try:

                    element.click()

                except:

                    driver.execute_script(
                        "arguments[0].click();",
                        element
                    )

                time.sleep(
                    1
                )

                print(
                    "Popup closed."
                )

                return True

            except:
                continue

    except Exception as e:

        print(
            "Popup detection error:",
            e
        )

    # --------------------------------------------------------
    # ID fallback
    # --------------------------------------------------------

    try:

        element = driver.find_element(
            By.ID,
            "txtt"
        )

        if element.is_displayed():

            driver.execute_script(
                "arguments[0].click();",
                element
            )

            time.sleep(
                1
            )

            print(
                "Popup closed using ID fallback."
            )

            return True

    except:
        pass

    return False


# ============================================================
# OPEN HOME
# ============================================================

def open_home(driver):

    print()
    print("=" * 75)
    print("OPENING GAIL GAS")
    print("=" * 75)

    driver.get(
        BASE_URL
    )

    WebDriverWait(
        driver,
        WAIT
    ).until(
        EC.presence_of_element_located(
            (
                By.TAG_NAME,
                "body"
            )
        )
    )

    time.sleep(
        3
    )

    close_popup(
        driver
    )

    time.sleep(
        1
    )


# ============================================================
# OPEN AREAS OF OPERATION
# ============================================================

def open_areas_menu(driver):

    print()
    print("=" * 75)
    print("OPENING AREAS OF OPERATION MENU")
    print("=" * 75)

    close_popup(
        driver
    )

    xpaths = [

        "//*[self::a or self::button or self::li]"
        "[contains("
        "translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'area of operation'"
        ")]",

        "//*[self::a or self::button or self::li]"
        "[contains("
        "translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'operation'"
        ")]",

        "//nav//*[self::a or self::button]"
        "[contains("
        "translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'operation'"
        ")]"
    ]

    # --------------------------------------------------------
    # Click approach
    # --------------------------------------------------------

    for xpath in xpaths:

        try:

            elements = driver.find_elements(
                By.XPATH,
                xpath
            )

            for element in elements:

                try:

                    text = clean_text(
                        element.text
                    )

                    if not text:
                        continue

                    print(
                        "Trying menu:",
                        repr(text)
                    )

                    driver.execute_script(
                        """
                        arguments[0].scrollIntoView({
                            block: 'center'
                        });
                        """,
                        element
                    )

                    time.sleep(
                        0.5
                    )

                    try:

                        element.click()

                    except:

                        driver.execute_script(
                            "arguments[0].click();",
                            element
                        )

                    time.sleep(
                        1.5
                    )

                    close_popup(
                        driver
                    )

                    menus = driver.find_elements(
                        By.CSS_SELECTOR,
                        "div.mega-menu"
                    )

                    for menu in menus:

                        try:

                            if menu.is_displayed():

                                print(
                                    "Areas menu opened."
                                )

                                return True

                        except:
                            continue

                except (
                    StaleElementReferenceException,
                    ElementClickInterceptedException
                ):

                    continue

        except:
            continue

    # --------------------------------------------------------
    # Hover fallback
    # --------------------------------------------------------

    print(
        "Click method did not open menu."
    )

    print(
        "Trying mouse hover..."
    )

    try:

        elements = driver.find_elements(
            By.XPATH,
            "//nav//*[self::a or self::li or self::div]"
        )

        for element in elements:

            try:

                text = clean_text(
                    element.text
                )

                if (
                    "operation"
                    not in text.lower()
                ):

                    continue

                ActionChains(
                    driver
                ).move_to_element(
                    element
                ).perform()

                time.sleep(
                    2
                )

                close_popup(
                    driver
                )

                menus = driver.find_elements(
                    By.CSS_SELECTOR,
                    "div.mega-menu"
                )

                for menu in menus:

                    try:

                        if menu.is_displayed():

                            print(
                                "Areas menu opened using hover."
                            )

                            return True

                    except:
                        continue

            except:
                continue

    except Exception as e:

        print(
            "Hover error:",
            e
        )

    return False


# ============================================================
# GET AREAS
# ============================================================

def get_areas(driver):

    print()
    print("=" * 75)
    print("STEP 1: GETTING AREAS OF OPERATION")
    print("=" * 75)

    if not open_areas_menu(
        driver
    ):

        print(
            "ERROR: Areas menu could not be opened."
        )

        with open(
            "gail_debug_home.html",
            "w",
            encoding="utf-8"
        ) as f:

            f.write(
                driver.page_source
            )

        return []

    # --------------------------------------------------------
    # Visible mega menu
    # --------------------------------------------------------

    mega_menu = None

    menus = driver.find_elements(
        By.CSS_SELECTOR,
        "div.mega-menu"
    )

    for menu in menus:

        try:

            if menu.is_displayed():

                mega_menu = menu

                break

        except:
            continue

    if mega_menu is None:

        print(
            "ERROR: Visible mega menu not found."
        )

        return []

    # --------------------------------------------------------
    # Area links
    # --------------------------------------------------------

    links = mega_menu.find_elements(
        By.CSS_SELECTOR,
        "a.listBigScreen"
    )

    print(
        "Area link elements:",
        len(links)
    )

    areas = []

    seen = set()

    for link in links:

        try:

            name = clean_text(
                link.text
            )

            if not name:
                continue

            if name.lower() == (
                "charge area status"
            ):

                continue

            if name not in seen:

                seen.add(
                    name
                )

                areas.append(
                    name
                )

        except:
            continue

    print()
    print(
        "TOTAL AREAS:",
        len(areas)
    )

    for i, area in enumerate(
        areas,
        1
    ):

        print(
            f"{i:02d}. {area}"
        )

    return areas


# ============================================================
# OPEN ONE AREA
# ============================================================

def open_area(
    driver,
    area
):

    print()
    print("-" * 75)
    print(
        f"OPENING AREA: {area}"
    )
    print("-" * 75)

    # --------------------------------------------------------
    # Return home
    # --------------------------------------------------------

    driver.get(
        BASE_URL
    )

    WebDriverWait(
        driver,
        WAIT
    ).until(
        EC.presence_of_element_located(
            (
                By.TAG_NAME,
                "body"
            )
        )
    )

    time.sleep(
        3
    )

    close_popup(
        driver
    )

    # --------------------------------------------------------
    # Open areas menu
    # --------------------------------------------------------

    if not open_areas_menu(
        driver
    ):

        raise Exception(
            "Could not open Areas menu"
        )

    # --------------------------------------------------------
    # Find area
    # --------------------------------------------------------

    target = None

    menus = driver.find_elements(
        By.CSS_SELECTOR,
        "div.mega-menu"
    )

    for menu in menus:

        try:

            if not menu.is_displayed():
                continue

            links = menu.find_elements(
                By.CSS_SELECTOR,
                "a.listBigScreen"
            )

            for link in links:

                try:

                    if (
                        clean_text(
                            link.text
                        )
                        == area
                    ):

                        target = link

                        break

                except:
                    continue

            if target is not None:
                break

        except:
            continue

    if target is None:

        raise Exception(
            f"Area not found: {area}"
        )

    # --------------------------------------------------------
    # Click area
    # --------------------------------------------------------

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        target
    )

    time.sleep(
        0.5
    )

    try:

        target.click()

    except:

        driver.execute_script(
            "arguments[0].click();",
            target
        )

    print(
        "Area clicked."
    )

    time.sleep(
        2
    )

    # --------------------------------------------------------
    # Popup after navigation
    # --------------------------------------------------------

    print(
        "Checking popup after area navigation..."
    )

    close_popup(
        driver
    )

    time.sleep(
        1
    )

    print(
        "Current URL:",
        driver.current_url
    )


# ============================================================
# OPEN CNG OUTLET
# ============================================================

def open_cng_outlet(
    driver
):

    print()
    print(
        "Opening CNG Outlet..."
    )

    close_popup(
        driver
    )

    time.sleep(
        1
    )

    # --------------------------------------------------------
    # Find CNG Outlet
    # --------------------------------------------------------

    try:

        WebDriverWait(
            driver,
            WAIT
        ).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[contains("
                    "translate(normalize-space(.),"
                    "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                    "'abcdefghijklmnopqrstuvwxyz'),"
                    "'cng outlet'"
                    ")]"
                )
            )
        )

    except TimeoutException:

        raise Exception(
            "CNG Outlet text not found."
        )

    elements = driver.find_elements(
        By.XPATH,
        "//*[contains("
        "translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
        "'abcdefghijklmnopqrstuvwxyz'),"
        "'cng outlet'"
        ")]"
    )

    target = None

    for element in elements:

        try:

            text = clean_text(
                element.text
            )

            if (
                text.lower()
                == "cng outlet"
            ):

                target = element

                break

        except:
            continue

    if target is None:

        raise Exception(
            "CNG Outlet card not found."
        )

    # --------------------------------------------------------
    # Parent card
    # --------------------------------------------------------

    try:

        card = target.find_element(
            By.XPATH,
            "./ancestor::mat-card[1]"
        )

    except:

        card = target

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        card
    )

    time.sleep(
        0.5
    )

    try:

        card.click()

    except:

        driver.execute_script(
            "arguments[0].click();",
            card
        )

    # --------------------------------------------------------
    # Wait CNG Stations
    # --------------------------------------------------------

    WebDriverWait(
        driver,
        WAIT
    ).until(
        EC.presence_of_element_located(
            (
                By.XPATH,
                "//*[contains("
                "translate(normalize-space(.),"
                "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
                "'abcdefghijklmnopqrstuvwxyz'),"
                "'cng stations'"
                ")]"
            )
        )
    )

    time.sleep(
        2
    )

    close_popup(
        driver
    )

    print(
        "CNG Stations section opened."
    )


# ============================================================
# FIND STATION DROPDOWN
# ============================================================

def find_station_select(
    driver
):

    selects = driver.find_elements(
        By.CSS_SELECTOR,
        "mat-select"
    )

    # --------------------------------------------------------
    # Known ID
    # --------------------------------------------------------

    for select in selects:

        try:

            select_id = (
                select.get_attribute(
                    "id"
                )
                or ""
            )

            if (
                select_id
                == "exampleFormControlSelect1"
            ):

                return select

        except:
            continue

    # --------------------------------------------------------
    # Text-based detection
    # --------------------------------------------------------

    for select in selects:

        try:

            text = clean_text(
                select.text
            )

            aria_label = (
                select.get_attribute(
                    "aria-label"
                )
                or ""
            )

            combined = (
                text
                + " "
                + aria_label
            ).lower()

            if (
                "location"
                in combined
                or
                "station"
                in combined
                or
                "cng"
                in combined
            ):

                return select

        except:
            continue

    # --------------------------------------------------------
    # Fallback
    # --------------------------------------------------------

    if selects:

        return selects[0]

    return None


# ============================================================
# GET STATION NAMES
# ============================================================

def get_station_names(
    driver
):

    print()
    print(
        "Reading CNG station dropdown..."
    )

    select = find_station_select(
        driver
    )

    if select is None:

        raise Exception(
            "CNG station dropdown not found."
        )

    driver.execute_script(
        """
        arguments[0].scrollIntoView({
            block: 'center'
        });
        """,
        select
    )

    time.sleep(
        0.5
    )

    try:

        select.click()

    except:

        driver.execute_script(
            "arguments[0].click();",
            select
        )

    WebDriverWait(
        driver,
        WAIT
    ).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                ".cdk-overlay-container mat-option"
            )
        )
    )

    options = driver.find_elements(
        By.CSS_SELECTOR,
        ".cdk-overlay-container mat-option"
    )

    stations = []

    for option in options:

        try:

            name = clean_text(
                option.text
            )

            if name:

                stations.append(
                    name
                )

        except:
            continue

    # --------------------------------------------------------
    # Close dropdown
    # --------------------------------------------------------

    try:

        driver.find_element(
            By.TAG_NAME,
            "body"
        ).send_keys(
            Keys.ESCAPE
        )

    except:
        pass

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    unique = []

    seen = set()

    for station in stations:

        if station not in seen:

            seen.add(
                station
            )

            unique.append(
                station
            )

    print(
        f"Stations found: {len(unique)}"
    )

    return unique


# ============================================================
# SELECT STATION
# ============================================================

def select_station(
    driver,
    station
):

    select = find_station_select(
        driver
    )

    if select is None:

        raise Exception(
            "Station selector not found."
        )

    try:

        select.click()

    except:

        driver.execute_script(
            "arguments[0].click();",
            select
        )

    WebDriverWait(
        driver,
        WAIT
    ).until(
        EC.presence_of_element_located(
            (
                By.CSS_SELECTOR,
                ".cdk-overlay-container mat-option"
            )
        )
    )

    options = driver.find_elements(
        By.CSS_SELECTOR,
        ".cdk-overlay-container mat-option"
    )

    selected = False

    # --------------------------------------------------------
    # Exact match
    # --------------------------------------------------------

    for option in options:

        try:

            text = clean_text(
                option.text
            )

            if text == station:

                driver.execute_script(
                    "arguments[0].click();",
                    option
                )

                selected = True

                break

        except:
            continue

    # --------------------------------------------------------
    # Partial match
    # --------------------------------------------------------

    if not selected:

        for option in options:

            try:

                text = clean_text(
                    option.text
                )

                if (
                    station.lower()
                    in text.lower()
                ):

                    driver.execute_script(
                        "arguments[0].click();",
                        option
                    )

                    selected = True

                    break

            except:
                continue

    if not selected:

        raise Exception(
            f"Could not select station: {station}"
        )

    time.sleep(
        1.5
    )


# ============================================================
# EXTRACT COORDINATES
# ============================================================

def extract_coordinates(
    maps_url
):

    if not maps_url:

        return "", ""

    # --------------------------------------------------------
    # Decode URL
    # --------------------------------------------------------

    url = unquote(
        maps_url
    )

    # Decode repeatedly in case
    # characters are encoded more than once

    for _ in range(3):

        decoded = unquote(
            url
        )

        if decoded == url:
            break

        url = decoded

    url = url.replace(
        "\xa0",
        " "
    )

    url = url.replace(
        "+",
        " "
    )

    # ========================================================
    # DECIMAL COORDINATES
    # ========================================================
    #
    # Example:
    #
    # ?q=28.9808388079645, 77.047706728816
    #
    # ========================================================

    decimal_patterns = [

        r"[?&]q\s*=\s*"
        r"([-+]?\d+(?:\.\d+)?)"
        r"\s*[,;]\s*"
        r"([-+]?\d+(?:\.\d+)?)",

        r"[?&]query\s*=\s*"
        r"([-+]?\d+(?:\.\d+)?)"
        r"\s*[,;]\s*"
        r"([-+]?\d+(?:\.\d+)?)",

        r"[?&]ll\s*=\s*"
        r"([-+]?\d+(?:\.\d+)?)"
        r"\s*[,;]\s*"
        r"([-+]?\d+(?:\.\d+)?)",

        r"/@"
        r"([-+]?\d+(?:\.\d+)?)"
        r","
        r"([-+]?\d+(?:\.\d+)?)"
    ]

    for pattern in decimal_patterns:

        match = re.search(
            pattern,
            url,
            re.IGNORECASE
        )

        if not match:
            continue

        try:

            latitude = float(
                match.group(1)
            )

            longitude = float(
                match.group(2)
            )

            if (
                -90 <= latitude <= 90
                and
                -180 <= longitude <= 180
            ):

                return (
                    str(latitude),
                    str(longitude)
                )

        except:
            pass

    # ========================================================
    # DMS COORDINATES
    # ========================================================
    #
    # Example:
    #
    # 28°59'59.1N 77°44'53.1E
    #
    # ========================================================

    dms_pattern = re.compile(
        r""
        r"(\d{1,3})"
        r"\s*(?:°|º)"
        r"\s*(\d{1,2})"
        r"\s*(?:'|′)"
        r"\s*(\d+(?:\.\d+)?)"
        r"\s*([NS])"
        r"\s+"
        r"(\d{1,3})"
        r"\s*(?:°|º)"
        r"\s*(\d{1,2})"
        r"\s*(?:'|′)"
        r"\s*(\d+(?:\.\d+)?)"
        r"\s*([EW])",
        re.IGNORECASE
    )

    match = dms_pattern.search(
        url
    )

    if match:

        try:

            lat_deg = float(
                match.group(1)
            )

            lat_min = float(
                match.group(2)
            )

            lat_sec = float(
                match.group(3)
            )

            lat_dir = (
                match.group(4)
                .upper()
            )

            lon_deg = float(
                match.group(5)
            )

            lon_min = float(
                match.group(6)
            )

            lon_sec = float(
                match.group(7)
            )

            lon_dir = (
                match.group(8)
                .upper()
            )

            latitude = (
                lat_deg
                + lat_min / 60
                + lat_sec / 3600
            )

            longitude = (
                lon_deg
                + lon_min / 60
                + lon_sec / 3600
            )

            if lat_dir == "S":

                latitude = -latitude

            if lon_dir == "W":

                longitude = -longitude

            return (
                f"{latitude:.8f}",
                f"{longitude:.8f}"
            )

        except:
            pass

    # ========================================================
    # ALTERNATIVE DMS
    # ========================================================
    #
    # Example:
    #
    # 28 59 59.1 N 77 44 53.1 E
    #
    # ========================================================

    alternative_dms = re.search(
        r""
        r"(\d{1,3})\s+"
        r"(\d{1,2})\s+"
        r"(\d+(?:\.\d+)?)\s*"
        r"([NS])"
        r"\s+"
        r"(\d{1,3})\s+"
        r"(\d{1,2})\s+"
        r"(\d+(?:\.\d+)?)\s*"
        r"([EW])",
        url,
        re.IGNORECASE
    )

    if alternative_dms:

        try:

            lat_deg = float(
                alternative_dms.group(1)
            )

            lat_min = float(
                alternative_dms.group(2)
            )

            lat_sec = float(
                alternative_dms.group(3)
            )

            lat_dir = (
                alternative_dms.group(4)
                .upper()
            )

            lon_deg = float(
                alternative_dms.group(5)
            )

            lon_min = float(
                alternative_dms.group(6)
            )

            lon_sec = float(
                alternative_dms.group(7)
            )

            lon_dir = (
                alternative_dms.group(8)
                .upper()
            )

            latitude = (
                lat_deg
                + lat_min / 60
                + lat_sec / 3600
            )

            longitude = (
                lon_deg
                + lon_min / 60
                + lon_sec / 3600
            )

            if lat_dir == "S":

                latitude = -latitude

            if lon_dir == "W":

                longitude = -longitude

            return (
                f"{latitude:.8f}",
                f"{longitude:.8f}"
            )

        except:
            pass

    # ========================================================
    # NOTHING FOUND
    # ========================================================

    return "", ""


# ============================================================
# FIND GOOGLE MAPS URL
# ============================================================

def find_map_url(
    driver
):

    # --------------------------------------------------------
    # Direct Google Maps selectors
    # --------------------------------------------------------

    selectors = [

        "a[href*='maps.google.com']",

        "a[href*='google.com/maps']",

        "a[href*='maps.google']",

        "a[href*='maps.app.goo.gl']",

        "a[href*='goo.gl/maps']"
    ]

    for selector in selectors:

        try:

            links = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            for link in links:

                try:

                    if not link.is_displayed():
                        continue

                    href = (
                        link.get_attribute(
                            "href"
                        )
                        or ""
                    )

                    if href:

                        return href

                except:
                    continue

        except:
            continue

    # --------------------------------------------------------
    # Locate Us
    # --------------------------------------------------------

    try:

        elements = driver.find_elements(
            By.XPATH,
            "//*[contains("
            "translate(normalize-space(.),"
            "'ABCDEFGHIJKLMNOPQRSTUVWXYZ',"
            "'abcdefghijklmnopqrstuvwxyz'),"
            "'locate us'"
            ")]"
        )

        for element in elements:

            try:

                if not element.is_displayed():
                    continue

                href = (
                    element.get_attribute(
                        "href"
                    )
                    or ""
                )

                if href:

                    return href

                parent = element.find_element(
                    By.XPATH,
                    "./ancestor::a[1]"
                )

                href = (
                    parent.get_attribute(
                        "href"
                    )
                    or ""
                )

                if href:

                    return href

            except:
                continue

    except:
        pass

    # --------------------------------------------------------
    # Search any href with coordinate pattern
    # --------------------------------------------------------

    try:

        links = driver.find_elements(
            By.TAG_NAME,
            "a"
        )

        for link in links:

            try:

                if not link.is_displayed():
                    continue

                href = (
                    link.get_attribute(
                        "href"
                    )
                    or ""
                )

                lower_href = (
                    href.lower()
                )

                if (
                    "?q=" in lower_href
                    or "&q=" in lower_href
                    or "?query=" in lower_href
                    or "&query=" in lower_href
                    or "?ll=" in lower_href
                    or "/@" in lower_href
                ):

                    return href

            except:
                continue

    except:
        pass

    return ""


# ============================================================
# EXTRACT STATION DATA
# ============================================================

def extract_station(
    driver,
    area,
    station
):

    address = ""

    # --------------------------------------------------------
    # Address
    # --------------------------------------------------------

    try:

        address_element = driver.find_element(
            By.CSS_SELECTOR,
            ".station-addres"
        )

        address = clean_text(
            address_element.text
        )

    except:

        try:

            elements = driver.find_elements(
                By.XPATH,
                "//*[contains(@class,'station-addres')]"
            )

            for element in elements:

                try:

                    if element.is_displayed():

                        address = clean_text(
                            element.text
                        )

                        break

                except:
                    continue

        except:
            pass

    # --------------------------------------------------------
    # Maps URL
    # --------------------------------------------------------

    maps_url = find_map_url(
        driver
    )

    # --------------------------------------------------------
    # Coordinates
    # --------------------------------------------------------

    latitude, longitude = (
        extract_coordinates(
            maps_url
        )
    )

    # --------------------------------------------------------
    # Console output
    # --------------------------------------------------------

    if maps_url:

        print(
            "      Maps URL:",
            maps_url
        )

    else:

        print(
            "      WARNING: Maps URL not found."
        )

    if latitude:

        print(
            "      Latitude:",
            latitude
        )

        print(
            "      Longitude:",
            longitude
        )

    else:

        print(
            "      WARNING: Coordinates not found."
        )

    return {

        "Area":
            area,

        "CNG Station Name":
            station,

        "Address":
            address,

        "Latitude":
            latitude,

        "Longitude":
            longitude,

        "Google Maps URL":
            maps_url,

        "Source URL":
            driver.current_url
    }


# ============================================================
# SCRAPE ONE AREA
# ============================================================

def scrape_area(
    driver,
    area
):

    records = []

    try:

        # ----------------------------------------------------
        # Open area
        # ----------------------------------------------------

        open_area(
            driver,
            area
        )

        close_popup(
            driver
        )

        # ----------------------------------------------------
        # CNG Outlet
        # ----------------------------------------------------

        open_cng_outlet(
            driver
        )

        # ----------------------------------------------------
        # Get stations
        # ----------------------------------------------------

        stations = get_station_names(
            driver
        )

        if not stations:

            print(
                "No CNG stations found."
            )

            return records

        # ----------------------------------------------------
        # Process stations
        # ----------------------------------------------------

        for index, station in enumerate(
            stations,
            start=1
        ):

            print()
            print(
                f"  [{index}/{len(stations)}] "
                f"{station}"
            )

            try:

                select_station(
                    driver,
                    station
                )

                # ------------------------------------------------
                # Wait for station address
                # ------------------------------------------------

                try:

                    WebDriverWait(
                        driver,
                        10
                    ).until(
                        lambda d:
                        clean_text(
                            d.find_element(
                                By.CSS_SELECTOR,
                                ".station-addres"
                            ).text
                        ) != ""
                    )

                except:
                    pass

                time.sleep(
                    0.5
                )

                record = extract_station(
                    driver,
                    area,
                    station
                )

                records.append(
                    record
                )

                print(
                    "      Address:",
                    record[
                        "Address"
                    ][:150]
                )

            except Exception as e:

                print(
                    "      ERROR:",
                    e
                )

                records.append({

                    "Area":
                        area,

                    "CNG Station Name":
                        station,

                    "Address":
                        "",

                    "Latitude":
                        "",

                    "Longitude":
                        "",

                    "Google Maps URL":
                        "",

                    "Source URL":
                        driver.current_url
                })

    except Exception as e:

        print()
        print(
            f"AREA ERROR: {e}"
        )

    return records


# ============================================================
# SAVE EXCEL AREA-WISE
# ============================================================

def safe_filename(name):
    """Create a Windows-safe filename from an area name."""
    name = clean_text(name)
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', ' ', name).strip()
    name = name.rstrip(".")
    return name or "Unknown_Area"


def save_area_excel(area_df, area):
    """
    Save one Excel file for one area.

    Example:
        GAIL_Gas_CNG_Outlets_Area_Wise/
            Delhi.xlsx
            Gurugram.xlsx
            Noida.xlsx
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    filename = f"GAIL_Gas_CNG_Outlets_{safe_filename(area)}.xlsx"
    output_file = os.path.join(OUTPUT_FOLDER, filename)

    # Keep only the required columns in the same order.
    required_columns = [
        "Area",
        "CNG Station Name",
        "Address",
        "Latitude",
        "Longitude",
        "Google Maps URL",
        "Source URL"
    ]

    for column in required_columns:
        if column not in area_df.columns:
            area_df[column] = ""

    area_df = area_df[required_columns].copy()

    # Clean values.
    for column in area_df.columns:
        area_df[column] = (
            area_df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Remove blank station names.
    area_df = area_df[
        area_df["CNG Station Name"] != ""
    ].copy()

    # Remove duplicates within this area only.
    before = len(area_df)

    area_df = area_df.drop_duplicates(
        subset=[
            "Area",
            "CNG Station Name",
            "Address"
        ],
        keep="first"
    )

    duplicates_removed = before - len(area_df)

    # Summary for this area.
    with_coordinates = len(
        area_df[
            (area_df["Latitude"] != "")
            &
            (area_df["Longitude"] != "")
        ]
    )

    summary_df = pd.DataFrame({
        "Metric": [
            "Source",
            "Source URL",
            "Area",
            "CNG Outlet Records",
            "Records With Coordinates",
            "Records Without Coordinates",
            "Duplicates Removed"
        ],
        "Value": [
            "GAIL Gas",
            BASE_URL,
            area,
            len(area_df),
            with_coordinates,
            len(area_df) - with_coordinates,
            duplicates_removed
        ]
    })

    print()
    print("=" * 75)
    print(f"SAVING AREA FILE: {area}")
    print(f"File: {output_file}")
    print("=" * 75)

    with pd.ExcelWriter(
        output_file,
        engine="openpyxl"
    ) as writer:

        area_df.to_excel(
            writer,
            sheet_name="CNG_Outlets",
            index=False
        )

        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

    # Format workbook.
    try:
        from openpyxl import load_workbook
        from openpyxl.utils import get_column_letter

        wb = load_workbook(output_file)

        for ws in wb.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions

            for column_cells in ws.columns:
                max_length = 0

                column_letter = get_column_letter(
                    column_cells[0].column
                )

                for cell in column_cells:
                    try:
                        length = len(str(cell.value))
                        if length > max_length:
                            max_length = length
                    except:
                        pass

                ws.column_dimensions[column_letter].width = min(
                    max(max_length + 2, 12),
                    70
                )

        wb.save(output_file)

    except Exception as e:
        print(
            "Excel formatting warning:",
            e
        )

    print(
        f"Saved: {os.path.abspath(output_file)}"
    )

    return output_file, len(area_df), duplicates_removed


def save_run_log(area_log):
    """
    Save only the processing log for the complete run.
    This is separate from the area-wise outlet files.
    """
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    log_file = os.path.join(
        OUTPUT_FOLDER,
        "Area_Log.xlsx"
    )

    log_df = pd.DataFrame(area_log)

    if not log_df.empty:
        log_df.to_excel(
            log_file,
            sheet_name="Area_Log",
            index=False
        )

    print(
        f"Area log saved: {os.path.abspath(log_file)}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    start_time = time.time()

    os.makedirs(
        OUTPUT_FOLDER,
        exist_ok=True
    )

    print(
        f"Area-wise output folder: "
        f"{os.path.abspath(OUTPUT_FOLDER)}"
    )

    driver = create_driver()

    area_log = []
    saved_files = []
    total_records = 0
    total_duplicates_removed = 0

    try:

        # ====================================================
        # OPEN HOME
        # ====================================================

        open_home(
            driver
        )

        # ====================================================
        # GET ALL AREAS
        # ====================================================

        areas = get_areas(
            driver
        )

        if not areas:

            print()
            print("=" * 75)
            print("NO AREAS FOUND.")
            print("=" * 75)

            return

        print()
        print("=" * 75)

        print(
            f"TOTAL AREAS TO PROCESS: "
            f"{len(areas)}"
        )

        print("=" * 75)

        # ====================================================
        # PROCESS EVERY AREA
        # ====================================================

        for area_index, area in enumerate(
            areas,
            start=1
        ):

            print()
            print(
                "#" * 75
            )

            print(
                f"PROCESSING AREA "
                f"{area_index}/{len(areas)}"
            )

            print(
                area
            )

            print(
                "#" * 75
            )

            records = scrape_area(
                driver,
                area
            )

            if records:

                # Save this area immediately.
                # No merged workbook is created.
                area_df = pd.DataFrame(records)

                output_file, record_count, duplicates_removed = (
                    save_area_excel(
                        area_df,
                        area
                    )
                )

                saved_files.append(output_file)
                total_records += record_count
                total_duplicates_removed += duplicates_removed

                area_log.append({

                    "Area":
                        area,

                    "Status":
                        "Success",

                    "CNG Outlets":
                        record_count,

                    "Duplicates Removed":
                        duplicates_removed,

                    "Output File":
                        output_file,

                    "Error":
                        ""
                })

            else:

                area_log.append({

                    "Area":
                        area,

                    "Status":
                        "Failed / No Data",

                    "CNG Outlets":
                        0,

                    "Duplicates Removed":
                        0,

                    "Output File":
                        "",

                    "Error":
                        "No records"
                })

            # Save the run log after every area so progress is preserved.
            save_run_log(area_log)

            time.sleep(
                PAGE_DELAY
            )

    finally:

        print()
        print(
            "Closing Chrome..."
        )

        driver.quit()

    # ========================================================
    # FINAL STATISTICS
    # ========================================================

    successful_areas = len([
        row for row in area_log
        if row["Status"] == "Success"
    ])

    failed_areas = (
        len(areas)
        - successful_areas
    )

    # Save final processing log.
    save_run_log(area_log)

    elapsed = (
        time.time()
        - start_time
    )

    print()
    print("#" * 75)
    print(
        "GAIL GAS CNG SCRAPING COMPLETED"
    )
    print("#" * 75)

    print(
        f"Areas found              : "
        f"{len(areas)}"
    )

    print(
        f"Successful areas         : "
        f"{successful_areas}"
    )

    print(
        f"Failed areas             : "
        f"{failed_areas}"
    )

    print(
        f"CNG outlet records      : "
        f"{total_records}"
    )

    print(
        f"Duplicates removed      : "
        f"{total_duplicates_removed}"
    )

    print(
        f"Area-wise files saved    : "
        f"{len(saved_files)}"
    )

    print(
        f"Output folder            : "
        f"{os.path.abspath(OUTPUT_FOLDER)}"
    )

    print(
        f"Time taken               : "
        f"{elapsed:.2f} seconds"
    )

    print("#" * 75)

    # ========================================================
    # FAILED AREAS
    # ========================================================

    if failed_areas > 0:

        print()
        print("=" * 75)
        print("FAILED / EMPTY AREAS")
        print("=" * 75)

        for row in area_log:

            if row["Status"] != "Success":

                print(
                    f"{row['Area']} -> "
                    f"{row['Error']}"
                )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()