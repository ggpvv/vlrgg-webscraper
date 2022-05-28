from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

def scrape_match(match_resp):
    row_data = {}
    if match_resp:
        match_soup = BeautifulSoup(match_resp.text, 'lxml')
        # MatchID
        row_data['matchID'] = (match_soup.find('input',
                                              attrs={'name': 'thread_id'})
                                              ['value'])
        # Date and Patch
        patch_date_header = match_soup.find('div', class_='match-header-date')
        row_data['Patch'] = (patch_date_header.find('div',
                                                   style='font-style: italic;')
                                                   .text.strip())
        row_data['Date'] = (patch_date_header.find('div',
                                                  class_='moment-tz-convert')
                                                  ['data-utc-ts'])
        #EventID, EventName, and EventStage
        event_header = match_soup.find('a', class_='match-header-event')
        eventid_pattern = re.compile('/(?P<eventid>\d+)/')
        row_data['EventID'] = (eventid_pattern.search(event_header['href'])
                                              .group('eventid'))
        row_data['EventName'] = (event_header.find('div',
                                                  style='font-weight: 700;')
                                            .text.strip())
        row_data['EventStage'] =  ' '.join((event_header.find('div',
                            class_='match-header-event-series')).text.split())

        team_header = match_soup.find('div', class_='match-header-vs')
        team1_info = team_header.find('a', class_='mod-1')
        team2_info = team_header.find('a', class_='mod-2')
        teamid_pattern = re.compile('/(?P<teamid>\d+)/')
        row_data['Team1ID'] = (teamid_pattern.search(team1_info['href'])
                                  .group('teamid'))
        row_data['Team2ID'] = (teamid_pattern.search(team2_info['href'])
                                   .group('teamid'))
        row_data['Team1'] = (team1_info.find('div',
                                             class_='wf-title-med')
                                            .text.strip())
        row_data['Team2'] = (team2_info.find('div',
                                             class_='wf-title-med')
                                            .text.strip())

    return row_data
