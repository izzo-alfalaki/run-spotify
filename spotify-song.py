from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
from datetime import datetime 

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--window-size=1300,800')

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 15)

url = 'https://open.spotify.com/section/0JQ5DB5E8N831KzFzsBBQ2' 

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
    artist = card.select_one('a[href^="/artist/"]')
    album = card.select_one('a[href^="/album/"]')
    img = card.find('img', {'data-testid': 'card-image'})

    data.append({
        'Title': title.get_text(strip=True) if title else None,
        'Artist': artist.get_text(strip=True) if artist else None,
        'Link': "https://open.spotify.com" + album['href'] if album else None,
        'Image': img['src'] if img else None,
        'Date': datetime.now(),
        'Category' : 'Trending Song'
    })

df = pd.DataFrame(data)
df['Rank'] = np.arange(1, len(df) + 1)

print("rows:", len(df))

import gspread as gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials

role = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

json_key = 'json_key.json'
credits = Credentials.from_service_account_file(json_key, scopes=role)
client = gspread.authorize(credits)

sh = client.open('Spotify')

try:
    work = sh.add_worksheet(title='Trending Song', cols = str(df.shape[1]), rows = str(df.shape[0]))
    set_with_dataframe(work, df)
except:
    work = sh.worksheet('Trending Song')
    append = df.copy()
    for col in append.select_dtypes(include=['datetime', 'datetimetz']).columns:
        append[col] = append[col].astype(str)

        work.append_rows(append.values.tolist(), value_input_option='USER_ENTERED')

