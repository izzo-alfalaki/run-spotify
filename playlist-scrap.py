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
import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials
from selenium.webdriver.common.keys import Keys

urls = [
    'https://open.spotify.com/playlist/37i9dQZEVXbJlfUljuZExa',
    'https://open.spotify.com/playlist/37i9dQZF1DWWuGaVZsglfu',
    'https://open.spotify.com/playlist/37i9dQZEVXbKcS4rq3mEhp',
    'https://open.spotify.com/playlist/37i9dQZF1DXb1RLKxkHZ77']

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--window-size=1920,1200')

service = Service('chromedriver.exe')
driver = webdriver.Chrome(service=service , options=options)

#pisau utk masuk hutan
wait = random.uniform(10,15)

data = []

for url in urls:
    print(url)
    driver.get(url)
    time.sleep(7)
    driver.save_screenshot('enter.png')

    html = driver.find_element(By.TAG_NAME, 'html')
    html.send_keys(Keys.END)

    time.sleep(10)
    driver.save_screenshot('scroll.png')

    html = BeautifulSoup(driver.page_source, 'html.parser')
    print('html retrieved') 
    
    #data-testid="entityTitle"
    #playlist image = src="https://charts-images.scdn.co/assets/locale_en/regional/weekly/region_my_default.jpg"
    #data-transition="sponsoredPlaylistHeaderText"

    playlist_name = html.find('h1')
    playlist_name = playlist_name.text.strip() if playlist_name else None
    #rows = html.find_all('div', {'role': 'row'})
    rows = html.select('div[role="row"]:has(a[data-testid="internal-track-link"])')
    for row in rows:
        img = row.find('img')
        img = img['src'] if img else None

        track = row.select_one('a[data-testid="internal-track-link"]')
        track = track.text.strip() if track else None

        artist = row.select_one('a[href^="/artist/"]')
        artist = artist.text.strip() if artist else None

        data.append({
            'Image': img,
            'Track': track,
            'Artist' : artist,
            'Playlist' : playlist_name,
            'Playlist Link' : url,
            'Datetime': datetime.now() }) 

driver.quit()

df = pd.DataFrame(data)
df['Rank per Playlist'] = df.groupby('Playlist Link').cumcount() % 30 + 1
print(f'{len(df)}')

import gspread
from gspread_dataframe import set_with_dataframe
from google.oauth2.service_account import Credentials

role = ['https://www.googleapis.com/auth/spreadsheets','https://www.googleapis.com/auth/drive']

json_key = 'izzo-472202-6ac4e89e0c3d.json'
credits = Credentials.from_service_account_file(json_key, scopes=role)
client = gspread.authorize(credits)

sh = client.open('Spotify')

try:
    work = sh.add_worksheet(title='Playlist', cols = str(df.shape[1]), rows = str(df.shape[0]))
    set_with_dataframe(work, df)
except:
    work = sh.worksheet('Playlist')
    append = df.copy()
    for col in append.select_dtypes(include=['datetime', 'datetimetz']).columns:
        append[col] = append[col].astype(str)
        work.append_rows(append.values.tolist(), value_input_option='USER_ENTERED')