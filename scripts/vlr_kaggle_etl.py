import json
import numpy as np
import pandas as pd
from pathlib import Path
import sqlite3

def etl():
    # specify variables to locate our data directory and target data file
    data_dir = Path.cwd().parent / 'data'
    val_data = data_dir / 'valorant.sqlite'

    # create a connection to the database and query the relevant data
    conn = sqlite3.connect(val_data)
    query = """
        SELECT EventName, Date, games.Team1, games.Team2, Winner, RoundHistory
        FROM game_rounds
        JOIN games USING (GameID)
        JOIN matches USING (MatchID)
        WHERE RoundHistory IS NOT NULL
    """
    df = pd.read_sql(query, conn)

    # fix the json string to use proper double quotes
    repl_dict = {"(\d+):" : r'"\1":',
                 "'(\S+)':" : r'"\1":',
                 "'([^,]+)'" : r'"\1"'}
    df['RoundHistory'] = df.RoundHistory.replace(regex=repl_dict)

    # convert the dataframe to a dictionary, iterate over every game and
    # then convert the json strings into a json object
    records = df.to_dict(orient='records')

    for game in records:
        try:
            game['RoundHistory'] = json.loads(game['RoundHistory'])
        except json.JSONDecodeError as err:
            print(f'{err.pos}\n{err.doc}\n{err.msg}')

    # convert back into a dataframe, using the nested json object to introduce
    # new columns, then pick out the relevant comments and dropping any rows
    # with null values
    cols = ['EventName', 'Date', 'Team1', 'Team2', 'Winner',
            'RoundHistory_12_ScoreAfterRound']
    df_half = pd.json_normalize(records, max_level=2, sep='_')[cols]
    df_half = df_half.rename(columns={
        'RoundHistory_12_ScoreAfterRound' : 'Half_Score'}).dropna()

    # create a column indicating if the team losing in the first half
    # ended up winning the game
    team1Wins = ['12-0', '11-1', '10-2', '9-3', '8-4', '7-5']
    df_half['Half_Winner'] = df_half.Team1.where(
        df_half['Half_Score'].isin(team1Wins), df_half.Team2)
    df_half['Comeback_Win'] = (df_half.Half_Winner != df_half.Winner)

    # replace and collapse mirror scores
    score_repl = {'0-12': '12-0', '1-11': '11-1', '2-10': '10-2', '3-9': '9-3',
                  '4-8': '8-4', '5-7': '7-5'}
    df_half['Half_Score'] = df_half.Half_Score.replace(to_replace=score_repl)

    # create a .csv of the cleaned dataframe
    df_half.to_csv(data_dir / 'val_comebacks.csv', index=False)

    
if __name__ == '__main__':
    etl()
