import pandas as pd


def load_data():

    df = pd.read_csv(
        "raw_data/steam_games.csv"
    )

    return df
