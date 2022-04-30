import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


def analysis():
    # read in data and convert half_score column to category data type
    data_dir = Path.cwd().parent / 'data'
    val_data = data_dir / 'val_comebacks.csv'
    score_categories = {'Half_Score': 'category'}
    df = pd.read_csv(val_data, dtype=score_categories)

    # create a dataframe which contains the ratios of the game results based
    # on their half score and if the losing first half team won the game
    df = score_comeback_win_ratio(df)
    sns.catplot(x='Comeback_Win', y='ratio', col='Half_Score',
                col_wrap=3, data=df, kind='bar')
    plt.show()


def score_comeback_win_ratio(df):
    # ignore matches which had a half score of 6-6 and
    # set a default order for the categories
    score_cat_order = ['7-5', '8-4', '9-3', '10-2', '11-1', '12-0']
    df['Half_Score'] = df.Half_Score.cat.set_categories(score_cat_order)
    df = df.dropna()

    column = ['ratio']
    df_comeback_ratio = pd.DataFrame(
        df.groupby('Half_Score')[['Comeback_Win']].value_counts(
            normalize=True),
        columns=column)
    return df_comeback_ratio.reset_index()


if __name__ == '__main__':
    analysis()
