import requests
from bs4 import BeautifulSoup
import re

def get_store_details(store_link):
    # store_link = "/ch/de_CH/store/36994/"
    store_url = f"https://www.trekbikes.com{store_link}"
    print(f"get_store_details: getting retailer details from: {store_url}")
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.82 Safari/537.36"}
    page = requests.get(store_url, headers=headers)
    soup = BeautifulSoup(page.content, "html5lib")

    store_details = []
    details = soup.find('div', attrs = {'class':['store-detail']})
    adress = details.find('ul', attrs = {'class':['store-detail__address']})
    
    telefon = adress.find('a')
    if telefon is not None:
        telefon = telefon.get_text().strip().replace("-", "").replace("+41", "").replace(" ", "")
        telefon = telefon if telefon[0] == "0" else f"0{telefon}"
        telefon = f"{telefon[0:3]} {telefon[3:6]} {telefon[6:8]} {telefon[8:10]}"
    else:
        telefon = ""
    
    plz_string = ""
    for adress_detail in adress.findAll('span', attrs = {'class':'text-weak'}):
        ads = adress_detail.get_text().strip()
        #\xA0
        p = re.compile(',\D(\d{4})\D+')
        m = p.match(ads)
        if m is not None:
            plz_string = m.group(1)
    plz = int(plz_string)
    
#    street = adress.find('span', attrs = {'class':'text-weak'}).get_text().strip()
    street_span = adress.findAll('li')[2]
    street_whitespaced = street_span.get_text().strip()
    street = " ".join(street_whitespaced.split())
    
    hours={}
    hours_table = details.find('table', attrs = {'qaid':['store-hours']})
    for tr in hours_table.findAll('tr'):
        day = tr.find('td', attrs = {'class':'store-hours__label'}).get_text().strip()
        val = tr.find('td', attrs = {'class':'store-hours__value'}).get_text().strip()
        p = re.compile('^([^\n]+)(\n\D+(\d[^\n]+))?$')
        m = p.match(val)
        if m.group(3) is None:
            hours[day] = m.group(1)
        else: 
            hours[day] = f"{m.group(1)}\n{m.group(3)}"

    links = details.find('div', attrs = {'class':['small-12 medium-5']})
    link = links.find("trek-link", attrs = {"id":"store-finder-get-directions"})
    if link is not None:
        link = link["href"]
    else:
        link = ""

    store_details = {
        "telefon": telefon,
        "street": street,
        "plz": plz,
        "hours": hours,
        "link": link
    }
    
    return store_details    

