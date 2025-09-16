from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
from tqdm import tqdm
from datetime import datetime

# Helper: Convert 12-hour time (e.g. "8:00 AM") to 24-hour format (e.g. "08:00")
def convert_to_24h(time_str):
    try:
        return datetime.strptime(time_str.strip(), "%I:%M %p").strftime("%H:%M")
    except:
        return None

# Setup Selenium
driver_path = "D:/heat/chromedriver.exe"
options = Options()
options.add_argument('--headless')
driver = webdriver.Chrome(service=Service(driver_path), options=options)

# Open the map view
url = "https://finder.nyc.gov/coolingcenters/locations?mView=map"
driver.get(url)
time.sleep(3)

# Load all locations by clicking 'Load all'
while True:
    try:
        more_button = driver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/ul/span/calcite-button")
        driver.execute_script("arguments[0].click();", more_button)
        print("🔁 Clicking 'Load all'...")
        time.sleep(5)
    except:
        print("✅ All centers loaded.")
        break

# Extract all location items
items = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div/div[3]/div[1]/ul/li")
print(f"✅ Total centers found: {len(items)}")

# Step 1: Basic info collection
centers = []
for item in tqdm(items):
    try:
        name = item.find_element(By.XPATH, ".//h3/a").text.strip()
        raw_category = item.find_element(By.XPATH, ".//p[1]/span").text.strip()
        location_id = item.get_attribute("data-locationid")
        button = item.find_element(By.XPATH, ".//calcite-button")
        href = driver.execute_script("return arguments[0].shadowRoot.querySelector('a').href", button)
        match = re.search(r"destination=([-.\d]+)%2C([-.\d]+)", href)
        lat, lon = (float(match.group(1)), float(match.group(2))) if match else (None, None)

        if " - " in raw_category:
            category, subcategory = raw_category.split(" - ", 1)
        else:
            category = raw_category
            subcategory = None

        centers.append({
            "Name": name,
            "Category": category,
            "Subcategory": subcategory,
            "Latitude": lat,
            "Longitude": lon,
            "LocationID": location_id
        })

    except Exception as e:
        print(f"[List error] {e}")
        continue

# Step 2: For each center, get day-by-day open/close hours
for center in tqdm(centers):
    try:
        detail_url = f"https://finder.nyc.gov/coolingcenters/locations/{center['LocationID']}"
        driver.get(detail_url)
        time.sleep(3)

        rows = driver.find_elements(By.CSS_SELECTOR, 'table#details-undefined tbody tr')
        for row in rows:
            try:
                day = row.find_element(By.TAG_NAME, "th").text.strip()
                time_text = row.find_element(By.TAG_NAME, "td").text.strip()
                if " - " in time_text:
                    open_raw, close_raw = time_text.split(" - ")
                    center[f"{day}_Open"] = convert_to_24h(open_raw)
                    center[f"{day}_Close"] = convert_to_24h(close_raw)
            except:
                continue

        # Return to the list
        driver.get(url)
        time.sleep(3)

    except Exception as e:
        print(f"[Detail error] {e}")
        continue

# Save results
driver.quit()
df = pd.DataFrame(centers)
df.to_csv("nyc_cooling_centers.csv", index=False)
print("✅ Finished: nyc_cooling_centers.csv")
