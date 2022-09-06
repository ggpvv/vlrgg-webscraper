import re

from bs4 import BeautifulSoup
import pandas as pd
import requests
from expression import Ok, Result, Error
from expression.extra.result import pipeline
from expression.collections import seq
from functools import partial

from vlrgg.utils import utils
from vlrgg.utils import functional_soup as fs

def match_data(match_soup):
    row_data = {}
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
        partial(fs.find_element, 'div', {'style': 'font-style: italic;'}),
        fs.inner_text)
    date_fn = pipeline(
        patch_date_header,
        partial(fs.find_element, 'div', {'class': 'moment-tz-convert'}),
        partial(fs.attribute, 'data-utc-ts'))
    row_data['Patch'] = patch_fn(match_soup)
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
        partial(fs.find_element, 'div', {'style': 'font-weight: 700;'}),
        fs.inner_text)
    eventstage_fn = pipeline(
        event_header,
        partial(fs.find_element,
                'div',
                {'class': 'match-header-event-series'}))
    row_data['EventID'] = eventid_fn(match_soup)
    row_data['EventName'] = eventname_fn(match_soup)
    row_data['EventStage'] = eventstage_fn(match_soup).map(utils.clean_stage)
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
        teamname,
        fs.inner_text)
    team2name_fn = pipeline(
        team2_info,
        teamname,
        fs.inner_text)
    row_data['Team1ID'] = team1id_fn(match_soup)
    row_data['Team2ID'] = team2id_fn(match_soup)
    row_data['Team1'] = team1name_fn(match_soup)
    row_data['Team2'] = team2name_fn(match_soup)
    # Map scores
    score_info = partial(fs.find_element,
                         'div',
                         {'class': 'match-header-vs-score'})
    score_strings = partial(fs.find_element, 'div', {'class': 'js-spoiler'})
    team_score_fn = pipeline(
        score_info,
        score_strings,
        fs.stripped_strings,
        )
    scores = team_score_fn(match_soup).map(lambda x: [y for y in x if y.isnumeric()])
    row_data['Team1_MapScore'] = scores.map(lambda x: x[0])
    row_data['Team2_MapScore'] = scores.map(lambda x: x[1])

    return row_data
    
def team_info(team_num, soup):
    info = pipeline(partial(fs.find_element,
                          'div',
                          {'class': 'match-header-vs'}),
                    partial(fs.find_element, 'a', {'class': f'mod-{team_num}'}))
    return info(soup)
    
                                                   
def team_id(team_num, soup):
    teamid_pattern = re.compile('/(?P<teamid>\d+)/')
    id_val = pipeline(
        partial(team_info, team_num),
        partial(fs.search_pattern, teamid_pattern))
    return id_val(soup)
    
    
def team_name(team_num, soup):
    name = pipeline(
        partial(team_info, team_num),
        partial(fs.find_element, 'div', {'class': 'wf-title-med'}),
        fs.inner_text)
    return name(soup)
    
    
def match_id(soup):
    return pipeline(
        partial(fs.find_element, 'input', {'name': 'thread_id'}),
        partial(fs.attribute, 'value'))(soup)
        
