import pandas as pd
import re

MAX_WORDS = 60

USELESS_TAGS = [
    "singleplayer",
    "multiplayer",
    "indie",
    "casual",
    "early access",
    "steam achievements",
    "steam cloud",
    "controller support"
]

def normalize_text(text):

    text = str(text).lower()

    text = text.replace("&", "and")

    text = re.sub(r"[^a-z0-9\s]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()

def truncate_words(text):

    words = str(text).split()

    return " ".join(words[:MAX_WORDS])

def clean_tags(text):

    if pd.isna(text):

        return ""

    tags = [
        t.strip()
        for t in str(text).split(",")
    ]

    tags = [
        t for t in tags
        if t.lower() not in USELESS_TAGS
    ]

    return ", ".join(tags)

def limpieza(df):

    df = df.copy()

    text_columns = [
        "name",
        "genre",
        "popular_tags",
        "game_description"
    ]

    for col in text_columns:

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .apply(normalize_text)
        )

    df["popular_tags"] = (
        df["popular_tags"]
        .apply(clean_tags)
    )

    df["game_description"] = (
        df["game_description"]
        .apply(truncate_words)
    )

    df["release_date"] = (
        df["release_date"]
        .astype(str)
        .str.extract(r'(\d{4})')
    )

    df["release_date"] = pd.to_numeric(
        df["release_date"],
        errors="coerce"
    ).fillna(0).astype(int)

    df["original_price"] = (
        df["original_price"]
        .replace({"Free": "0"})
        .astype(str)
        .str.replace("$", "", regex=False)
    )

    df["original_price"] = pd.to_numeric(
        df["original_price"],
        errors="coerce"
    ).fillna(0)

    df["embedding"] = (

        (df["name"] + ". ") * 3 +

        (df["genre"] + ". ") * 2 +

        (df["popular_tags"] + ". ") * 2 +

        df["game_description"]

    )

    return df.reset_index(drop=True)
