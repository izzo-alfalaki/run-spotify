from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import time
import random
from datetime import datetime 

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--window-size=1300,800')

serv = Service('chromedriver.exe')
driver = webdriver.Chrome(service=serv, options=options)
wait = WebDriverWait(driver, 15)

#url = 'https://open.spotify.com/section/0JQ5DB5E8N831KzFzsBBQ2' # song 
url = 'https://open.spotify.com/section/0JQ5DAnM3wGh0gz1MXnu3C' # artist
#url ='https://open.spotify.com/section/0JQ5DAnM3wGh0gz1MXnu3B' # album, 
#url = 'https://open.spotify.com/section/0JQ5DAnM3wGh0gz1MXnu4h'] # radio 
            
driver.get(url)
wait = WebDriverWait(driver, 25)
wait
driver.save_screenshot('Home-Spotify.png')

html = BeautifulSoup(driver.page_source, 'html.parser')
driver.quit()

cards = html.find_all('div', {'data-encore-id': 'card'})

data = []

for card in cards:
    title = card.find('p', {'data-encore-id': 'cardTitle'})
    artist = card.find('p', title = True)
    img = card.find('img', {'data-testid': 'card-image'})
    
    #https://open.spotify.com/search/tribe%20called%20quest
    link = artist['title'] if artist else None

    data.append({
        'Artist': title.get_text(strip=True) if artist else None,
        'Title': artist.get_text(strip = True) if artist else None,
        'Link': "https://open.spotify.com/search/" + link.replace(' ','%20') ,
        'Image': img['src'] if img else None,
        'Date': datetime.now(),
        'Category' : 'Trending Artist'
    })

df = pd.DataFrame(data)
df['Rank']= np.arange(1, len(df)+1)
#print(df)
print("rows:", len(df))

import pandas as pd
import gspread as gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials

role = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

json_key = 'izzo-472202-6ac4e89e0c3d.json'
credits = Credentials.from_service_account_file(json_key, scopes=role)
client = gspread.authorize(credits)

sh = client.open('Spotify')

from gspread_dataframe import set_with_dataframe

try:
    work = sh.add_worksheet(title='Trending Artist', cols = str(df.shape[1]), rows = str(df.shape[0]))
    set_with_dataframe(work, df)
except:
    work = sh.worksheet('Trending Artist')
    append = df.copy()
    for col in append.select_dtypes(include=['datetime', 'datetimetz']).columns:
        append[col] = append[col].astype(str)
        work.append_rows(append.values.tolist(), value_input_option='USER_ENTERED')