# GAIL Gas CNG Outlet Scraper

Selenium automation for navigating the GAIL Gas website, discovering available areas, selecting CNG outlet listings, and saving station details in area-wise Excel workbooks.

## How it works

1. Opens the source website in a visible Chrome browser.
2. Handles the page popup, navigates the areas-of-operation menu, and enters the CNG outlet workflow.
3. Discovers available areas and station options from the rendered site.
4. Extracts available outlet details, including address and map-link information, while preserving the associated area and source URL.
5. Cleans blank station names, deduplicates records within each area, and writes an Excel workbook per area plus a processing log.

## Area workbook contents

Each GAIL_Gas_CNG_Outlets_<Area>.xlsx workbook is saved under GAIL_Gas_CNG_Outlets_Area_Wise/ and contains:

- CNG_Outlets — Area, CNG Station Name, Address, Latitude, Longitude, Google Maps URL, and Source URL
- Summary — source URL, area name, outlet record count, coordinate completeness, and duplicates removed

The script also writes Area_Log.xlsx with the per-area processing log. Individual areas are saved as they are processed, so completed area outputs can remain available if a later area fails.

## Files

- GAIL_Gas_CNG_Outlets_Area_Wise.py — scraper entry point
- An example area workbook — sample output dataset
- requirements.txt — Python dependencies

## Requirements and setup

- Python 3.10 or a compatible version
- Google Chrome
- Selenium, pandas, and openpyxl from requirements.txt

    python -m venv .venv
    .venv/Scripts/Activate.ps1
    pip install -r requirements.txt

## Run

    python GAIL_Gas_CNG_Outlets_Area_Wise.py

The output folder is configured by OUTPUT_FOLDER near the top of the script. It is created relative to the current working directory unless you change that value.

## Notes

- The browser is visible by default; headless mode is commented out in the script.
- Navigation relies on current website menus, selectors, and station controls, so markup changes may require maintenance.
- Check the source website's terms and applicable policies before using or redistributing collected data.
