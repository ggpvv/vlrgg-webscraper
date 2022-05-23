from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

def scrape_matches(match_resp):
    row_data = {}
    if match_resp:
        match_soup = BeautifulSoup(match_resp.text, 'lxml')

        # MatchID


    return row_data
