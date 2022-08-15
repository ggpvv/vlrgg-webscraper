import re

from bs4 import BeautifulSoup
import pandas as pd
import requests
from expression import Ok, Result, Error
from expression.extra.result import pipeline
from functools import partial

from utils import utils
from utils import functional_soup as fs

def get_match(match_soup):
    row_data = {}
    def strip_text(x): return x.text.strip()
    def clean_stage(x): return ' '.join(x.text.split())
    # MatchID
    matchid_fn = pipeline(
        partial(fs.find_element, 'input', {'name': 'thread_id'}),
        partial(fs.attribute, 'value'))
    row_data['matchID'] = matchid_fn(match_soup)
    # Patch and Date
    patch_date_header = partial(fs.find_element,
                                'div',
                                {'class': 'match-header-date'})
    patch_fn = pipeline(
        patch_date_header,
        partial(fs.find_element, 'div', {'style': 'font-style: italic;'}))
    date_fn = pipeline(
        patch_date_header,
        partial(fs.find_element, 'div', {'class': 'moment-tz-convert'}),
        partial(fs.attribute, 'data-utc-ts'))
    row_data['Patch'] = patch_fn(match_soup).map(strip_text)
    row_data['Date'] = date_fn(match_soup)
    # EventID, EventName, EventStage
    event_header = partial(fs.find_element,
                           'a',
                           {'class': 'match-header-event'})
    eventid_pattern = re.compile('/(?P<eventid>\d+)/')
    eventid_fn = pipeline(
        event_header,
        partial(fs.attribute, 'href'),
        partial(fs.search_pattern, eventid_pattern))
    eventname_fn = pipeline(
        event_header,
        partial(fs.find_element, 'div', {'style': 'font-weight: 700;'}))
    eventstage_fn = pipeline(
        event_header,
        partial(fs.find_element,
                'div',
                {'class': 'match-header-event-series'}))
    row_data['EventID'] = eventid_fn(match_soup)
    row_data['EventName'] = eventname_fn(match_soup).map(strip_text)
    row_data['EventStage'] = eventstage_fn(match_soup).map(clean_stage)
    # Team IDs and Names
    team_header = partial(fs.find_element,
                          'div',
                          {'class': 'match-header-vs'})
    team1_info = pipeline(
        team_header,
        partial(fs.find_element, 'a', {'class': 'mod-1'}))
    team2_info = pipeline(
        team_header,
        partial(fs.find_element, 'a', {'class': 'mod-2'}))
    teamid_pattern = re.compile('/(?P<teamid>\d+)/')
    team1id_fn = pipeline(
        team1_info,
        partial(fs.search_pattern, teamid_pattern))
    team2id_fn = pipeline(
        team2_info,
        partial(fs.search_pattern, teamid_pattern))
    teamname = partial(fs.find_element, 'div', {'class': 'wf-title-med'})
    team1name_fn = pipeline(
        team1_info,
        teamname)
    team2name_fn = pipeline(
        team2_info,
        teamname)
    row_data['Team1ID'] = team1id_fn(match_soup)
    row_data['Team2ID'] = team2id_fn(match_soup)
    row_data['Team1'] = team1name_fn(match_soup).map(strip_text)
    row_data['Team2'] = team2name_fn(match_soup).map(strip_text)

    return row_data
