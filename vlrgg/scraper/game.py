from collections import namedtuple
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re
from expression import Ok, Result, Error, pipe, compose
from expression.collections import seq, block
from expression.core import result
from expression.extra.result import pipeline
from functools import partial

from vlrgg.utils import utils, functional_soup as fs
from vlrgg.utils import functional_regex as fre
from vlrgg.scraper import match


def game_data(game_soup):
    row_data = {}
    stats = partial(
                fs.find_element, 'div', {'class': 'vm-stats-game mod-active'}
            )
    overview_soup = stats(game_soup)
    # Team divs
    team1_div = partial(fs.find_element, 'div', {'class': 'team'})
    team2_div = partial(fs.find_element, 'div', {'class': 'team mod-right'})
    score_div = partial(fs.find_element, 'div', {'class': 'score'})
    team1_score = pipeline(
                team1_div,
                score_div,
                fs.inner_text
                )
    team2_score = pipeline(
                team2_div,
                score_div,
                fs.inner_text
                )
   
    # GameID and MatchID
    row_data['GameID'] = overview_soup.bind(
                                       partial(fs.attribute, 'data-game-id')
                                       )
    row_data['MatchID'] = match.match_id(game_soup)
    # Map
    map_name = pipeline(
            partial(fs.find_element, 'div', {'class': 'map'}),
            partial(fs.find_element, 'span', {}),
            fs.stripped_strings)
    row_data['Map'] = overview_soup.bind(map_name).map(
                    lambda x: x[0])
    # Team IDs
    row_data['Team1ID'] = match.team_id(1, game_soup)
    row_data['Team2ID'] = match.team_id(2, game_soup)
    # Team names and winner
    row_data['Team1'] = match.team_name(1, game_soup)
    row_data['Team2'] = match.team_name(2, game_soup)
    
    def is_winner(team_div):
        score_div = team_div.bind(partial(fs.find_element, 'div', {'class': 'mod-win'}))
        match score_div:
            case Ok():
                return True
            case _:
                return False
                    
    row_data['Winner'] = (row_data['Team1'] 
                            if is_winner(overview_soup.bind(team1_div))
                            else row_data['Team2']
                         )
    # Team total rounds
    row_data['Team1TotalRounds'] = overview_soup.bind(team1_score)
    row_data['Team2TotalRounds'] = overview_soup.bind(team2_score)
    # Half scores and sides
    team1_half_rounds_fn = pipeline(
                  team1_div,
                  partial(fs.find_elements, 'span', {})
                  )
    team2_half_rounds_fn = pipeline(
                  team2_div,
                  partial(fs.find_elements, 'span', {})
                  )
    
    def side(attribute):
        result = 'attack' if attribute == 'mod-t' else 'defense'
        return result
    
    first_half_side = compose(
                seq.head,
                partial(fs.attribute, 'class'),
                result.map(lambda x: x[0])
                )    			
    row_data['Team1_SideFirstHalf'] = overview_soup.bind(
                        pipeline(
                            team1_half_rounds_fn,
                            first_half_side
                            )
                        ).map(side)
    row_data['Team2_SideFirstHalf'] = overview_soup.bind(
                        pipeline(
                            team2_half_rounds_fn,
                            first_half_side
                            )
                        ).map(side)
    first_half = compose(seq.head,
                         fs.inner_text
                 )
    second_half = compose(seq.tail,
                          seq.head,
                          fs.inner_text
                  )
    ot_rounds = pipeline(partial(fs.find_element, 'div', {'class': 'mod-ot'}),
                         fs.inner_text
                )
    row_data['Team1_RoundsFirstHalf'] = overview_soup.bind(
                                            pipeline(
                                                team1_half_rounds_fn,
                                                first_half
                                            )
                                        )
    row_data['Team1_RoundsSecondHalf'] = overview_soup.bind(
                                            pipeline(
                                                team1_half_rounds_fn,
                                                second_half
                                            )
                                        )
    row_data['Team1_RoundsOT'] = overview_soup.bind(
                                     pipeline(
                                         team1_div,
                                         ot_rounds
                                     )
                                 )
    row_data['Team2_RoundsFirstHalf'] = overview_soup.bind(
                                            pipeline(
                                                team2_half_rounds_fn,
                                                first_half
                                            )
                                        )
    row_data['Team2_RoundsSecondHalf'] = overview_soup.bind(
                                            pipeline(
                                                team2_half_rounds_fn,
                                                second_half
                                            )
                                        )
    row_data['Team2_RoundsOT'] = overview_soup.bind(
                                     pipeline(
                                         team2_div,
                                         ot_rounds
                                     )
                                 )    
    # econ round stats
    def insert_gameid(game_id, url):
        return game_id.map(lambda x: f'{url}?game={x}&tab=economy')

    econ_url = row_data['MatchID'].bind(
                                      compose(
                                        lambda x: f'https://vlr.gg/{x}/',
                                        partial(insert_gameid,
                                                row_data['GameID']
                                        )
                                      )
    )
    econ_table = compose(
                    pipeline(
                        utils.html_text,
                        stats,
                        partial(fs.find_element, 'table', {
                         'class': 'wf-table-inset mod-econ'
                         }
                        ),
                        partial(fs.find_elements, 'tr', {})
                    ),
                    result.map(compose(block.of_seq, block.tail))
                 )

    team1_stats = result.map(block.head)
    team2_stats = result.map(compose(block.tail, block.head))
    econ_stats_cells = compose(
                           result.bind(partial(fs.find_elements, 'td', {})),
                           result.map(compose(block.of_seq, block.tail))
                       )
    econ_pattern = re.compile(r'(?P<total>\d+)\t+\((?P<won>\d+)\)')
    rounds = result.bind(
                 pipeline(
                     fs.inner_text,
                     partial(fre.search_pattern, econ_pattern),
                     partial(fre.re_match_group, 'total')
                 )
            )
    won = result.bind(
              pipeline(
                  fs.inner_text,
                  partial(fre.search_pattern, econ_pattern),
                  partial(fre.re_match_group, 'won')
              )
          )
    team1_econ_stats = econ_url.bind(
                                    compose(
                                        econ_table, team1_stats, econ_stats_cells
                                    )
                                )
    team2_econ_stats = econ_url.bind(
                                    compose(
                                        econ_table, team2_stats, econ_stats_cells
                                    )
                                )
    # functions for the economy columns
    team1_pistol = compose(
                       result.map(block.item(0)),
                       result.bind(fs.inner_text)
                   )
    team2_pistol = compose(
                       result.map(block.item(0)),
                       result.bind(fs.inner_text)
                   )
    team1_eco_total = compose(
                       result.map(block.item(1)),
                       rounds
                   )
    team2_eco_total = compose(
                       result.map(block.item(1)),
                       rounds
                   )
    team1_eco_won = compose(
                       result.map(block.item(1)),
                       won
                   )
    team2_eco_won = compose(
                       result.map(block.item(1)),
                       won
                   )
    team1_semieco_total = compose(
                       result.map(block.item(2)),
                       rounds
                   )
    team2_semieco_total = compose(
                       result.map(block.item(2)),
                       rounds
                   )
    team1_semieco_won = compose(
                       result.map(block.item(2)),
                       won
                   )
    team2_semieco_won = compose(
                       result.map(block.item(2)),
                       won
                   )
    team1_semibuy_total = compose(
                       result.map(block.item(3)),
                       rounds
                   )
    team2_semibuy_total = compose(
                       result.map(block.item(3)),
                       rounds
                   )
    team1_semibuy_won = compose(
                       result.map(block.item(3)),
                       won
                   )
    team2_semibuy_won = compose(
                       result.map(block.item(3)),
                       won
                   )
    team1_fullbuy_total = compose(
                       result.map(block.item(4)),
                       rounds
                   )
    team2_fullbuy_total = compose(
                       result.map(block.item(4)),
                       rounds
                   )
    team1_fullbuy_won = compose(
                       result.map(block.item(4)),
                       won
                   )
    team2_fullbuy_won = compose(
                       result.map(block.item(4)),
                       won
                   )
    row_data['Team1_Pistol_Won'] = team1_pistol(team1_econ_stats)
    row_data['Team2_Pistol_Won'] = team2_pistol(team2_econ_stats)
    row_data['Team1_Eco_Total'] = team1_eco_total(team1_econ_stats)
    row_data['Team1_Eco_Won'] = team1_eco_won(team1_econ_stats)
    row_data['Team2_Eco_Total'] = team2_eco_total(team2_econ_stats)
    row_data['Team2_Eco_Won'] = team2_eco_won(team2_econ_stats)
    row_data['Team1_Semieco_Total'] = team1_semieco_total(team1_econ_stats)
    row_data['Team1_Semieco_Won'] = team1_semieco_won(team1_econ_stats)
    row_data['Team2_Semieco_Total'] = team2_semieco_total(team2_econ_stats)
    row_data['Team2_Semieco_Won'] = team2_semieco_won(team2_econ_stats)
    row_data['Team1_Semibuy_Total'] = team1_semibuy_total(team1_econ_stats)
    row_data['Team1_Semibuy_Won'] = team1_semibuy_won(team1_econ_stats)
    row_data['Team2_Semibuy_Total'] = team2_semibuy_total(team2_econ_stats)
    row_data['Team2_Semibuy_Won'] = team2_semibuy_won(team2_econ_stats)
    row_data['Team1_Fullbuy_Total'] = team1_fullbuy_total(team1_econ_stats)
    row_data['Team1_Fullbuy_Won'] = team1_fullbuy_won(team1_econ_stats)
    row_data['Team2_Fullbuy_Total'] = team2_fullbuy_total(team2_econ_stats)
    row_data['Team2_Fullbuy_Won'] = team2_fullbuy_won(team2_econ_stats)
    columns = list(row_data.keys())
    GameRow = namedtuple('GameRow', columns)
    return GameRow(**row_data)
                         
