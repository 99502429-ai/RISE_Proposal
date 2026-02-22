import pandas as pd
import numpy as np
import tasks.ChanScraper as chan
import tasks.ChanCleaner as clean
import urllib, json, os
from datetime import datetime
import time
from urllib.error import HTTPError

os.chdir('src')

def scrape_pol() -> None:
    chan.all_4chan_to_csv("pol", './data/raw')
    print(f'Cleaning data...')
    df = clean.full_clean('./data/raw')
    df.to_csv('./data/clean/pol_clean.csv', index=False)

scrape_pol()