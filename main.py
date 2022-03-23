import requests
from bs4 import BeautifulSoup
import store_details
import pandas as pd
import json
import time



stores = []
trek_homepage = "https://www.trekbikes.com"

for nr in range(0, 5):
#for nr in range(0, 1):
    print(f"nr: {nr}")
    url = f"{trek_homepage}/ch/de_CH/store-finder/retailer/CH/{nr}/"
    print(f"main: getting list of retailers from {url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36"}
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.content, "html5lib")
    for columns in soup.findAll('div', attrs = {'class':['row row--full']}):
        #i=0
        for row in columns.findAll('li', attrs = {'class':['region__list-item']}):
            #i=i+1
            #if i>2: break
            store_city = row.find('span', attrs = {'class':'text-strong'}).get_text().strip().replace(",","")
            store_name = row.find('span', attrs = {'class':'text-weak'}).get_text().strip()
            store_link = row.find('a', attrs = {'class':'country__link link-weak'})["href"]
            details = store_details.get_store_details(store_link)
            store = {
                "Stadt":store_city,
                "Name":store_name,
                "Telefon": details["telefon"],
                "PLZ": details["plz"],
                "Strasse": details["street"],
                "Auf Lager": "",
                "Komment": "",
                "Website": details["link"],
                "Trek Website": f"{trek_homepage}{store_link}",
                "Montag": details["hours"]["Montag"],
                "Dienstag": details["hours"]["Dienstag"],
                "Mittwoch": details["hours"]["Mittwoch"],
                "Donnerstag": details["hours"]["Donnerstag"],
                "Freitag": details["hours"]["Freitag"],
                "Samstag": details["hours"]["Samstag"],
                "Sonntag": details["hours"]["Sonntag"],
            }
            stores.append(store)
            print("main: sleep")
            time.sleep(1.1)

df_stores = pd.DataFrame.from_dict(stores)

print("main: getting postleitzahl to kanton mapping")
with open(r'resources\plz_verzeichnis_v2.json') as data_file:    
    data = json.load(data_file)  
df_plz_kanton = pd.json_normalize(data)[['fields.postleitzahl','fields.kanton']]
df_plz_kanton["fields.postleitzahl"] = df_plz_kanton["fields.postleitzahl"].astype(int)
df_plz_kanton = df_plz_kanton.drop_duplicates()

print(f"main: df_stores.shape: {df_stores.shape}")
print(f"main: df_plz_kanton.shape: {df_plz_kanton.shape}")
print("main: merging retailer df with mapping")
df = pd.merge(df_stores, df_plz_kanton, "left", left_on="PLZ", right_on="fields.postleitzahl")
df = df[[
    "Stadt",
    "Name",
    "Telefon",
    "fields.kanton",
    "PLZ",
    "Strasse",
    "Auf Lager",
    "Komment",
    "Montag",
    "Dienstag",
    "Mittwoch",
    "Donnerstag",
    "Freitag",
    "Samstag",
    "Sonntag",
    "Website",
    "Trek Website",
    ]]
df = df.rename(columns={"fields.kanton": "Kanton"})
df.index = df.index + 1
print(f"main: df.shape: {df.shape}")

print(f"main: saving to excel")
df.to_excel("trek_handlers_ch.xlsx")
