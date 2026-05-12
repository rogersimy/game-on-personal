import pandas as pd


def limpieza(df):

    df = df.copy()

    df.columns = (
        df.columns
        .str.lower()
    )

    # =========================
    # PRICE
    # =========================

    if "price" not in df.columns:

        df["price"] = "0"

    df["price"] = (
        df["price"]
        .astype(str)
        .str.replace("$", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.strip()
    )

    df["price_num"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    ).fillna(0)

    # =========================
    # YEAR
    # =========================

    if "release_date" in df.columns:

        df["release_date"] = pd.to_datetime(
            df["release_date"],
            errors="coerce"
        )

        df["year"] = (
            df["release_date"]
            .dt.year
            .fillna(0)
            .astype(int)
        )

    else:

        df["year"] = 0

    # =========================
    # TEXT COLUMNS
    # =========================

    text_columns = [
        "name",
        "genres",
        "tags",
        "game_details"
    ]

    for col in text_columns:

        if col not in df.columns:

            df[col] = ""

        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.lower()
        )

    # =========================
    # CONTENT TYPE
    # =========================

    if "required_age" in df.columns:

        df["content_type"] = (
            df["required_age"]
            .apply(
                lambda x:
                "adult"
                if pd.to_numeric(
                    x,
                    errors="coerce"
                ) >= 18
                else "general"
            )
        )

    else:

        df["content_type"] = "general"

    # =========================
    # COMBINED TEXT
    # =========================

    df["combined_text"] = (

        df["name"] + " " +

        df["genres"] + " " +

        df["tags"] + " " +

        df["game_details"]

    )

    return df
