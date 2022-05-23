from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

root_url = 'https://www.vlr.gg'
events_url = root_url + '/events/'
event_root_url = 'https://www.vlr.gg/event/'

def event_games(event, table_names):
    vlr_session = requests.Session()
    headers = {}
    vlr_session.headers.update(headers)
    df_dict = {}

    events_resp = vlr_session.get(events_url)
    main_url = _event_url(event, events_resp)
    if main_url is not None:
        matches_url = (main_url.replace('event', 'event/matches')
                       + '/&group=completed')
        matches_resp = vlr_session.get(matches_url)
        match_urls = _event_match_urls(matches_resp)
        """
        for match_url in match_urls:
            match_resp = vlr_session.get('match_url)
            for table_name in table_names:
                table_data = function_map[table_name](match_resp)
                for k, v in table_data.items():
                    df_dict[table_name][k].append(v)
        """

    return df_dict


def _event_url(event, events_resp):
    url_string = None
    if re.match('(\d+)', event):
        url_string = event_root_url + event

    return url_string


def _event_match_urls(matches_resp):
    urls = []
    if matches_resp:
        matches_soup = BeautifulSoup(matches_resp.text, 'lxml')
        match_items = matches_soup.find_all('a', 'match-item')
        urls = [match_item['href'] for match_item in match_items]

    return urls
