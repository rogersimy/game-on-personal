import numpy as np

from sklearn.metrics.pairwise import (
    cosine_similarity
)

from pln_model.query_rewriter import (
    rewrite_query
)


def query_games(
    query,
    df,
    embeddings,
    model,
    n_top=5,
    genre=None,
    content_type=None,
    min_price=0,
    max_price=999,
    min_year=1970,
    max_year=2030
):

    # =========================
    # QUERY REWRITE
    # =========================

    rewritten_query = rewrite_query(
        query
    )

    # =========================
    # FILTERS
    # =========================

    filtered_df = df.copy()

    filtered_df = filtered_df[

        (
            filtered_df["price_num"]
            >= min_price
        ) &

        (
            filtered_df["price_num"]
            <= max_price
        ) &

        (
            filtered_df["year"]
            >= min_year
        ) &

        (
            filtered_df["year"]
            <= max_year
        )

    ]

    if genre and genre != "all":

        filtered_df = filtered_df[
            filtered_df["genres"]
            .str.contains(
                genre,
                case=False,
                na=False
            )
        ]

    if (
        content_type and
        content_type != "all"
    ):

        filtered_df = filtered_df[
            filtered_df["content_type"]
            == content_type
        ]

    if len(filtered_df) == 0:

        return [], rewritten_query

    # =========================
    # ALIGN EMBEDDINGS
    # =========================

    filtered_indices = (
        filtered_df.index.to_numpy()
    )

    filtered_indices = filtered_indices[
        filtered_indices < len(embeddings)
    ]

    filtered_df = filtered_df.loc[
        filtered_indices
    ]

    filtered_embeddings = embeddings[
        filtered_indices
    ]

    # =========================
    # QUERY EMBEDDING
    # =========================

    query_embedding = model.encode(
        [rewritten_query],
        normalize_embeddings=True
    )

    similarities = cosine_similarity(
        query_embedding,
        filtered_embeddings
    )[0]

    filtered_df = filtered_df.copy()

    filtered_df["similarity"] = similarities

    # =========================
    # NAME BOOST
    # =========================

    boosts = []

    query_words = (
        query.lower().split()
    )

    for _, row in filtered_df.iterrows():

        boost = 0

        game_name = str(
            row["name"]
        ).lower()

        for word in query_words:

            if word in game_name:

                boost += 0.08

        boosts.append(boost)

    filtered_df["boost"] = boosts

    filtered_df["final_score"] = (

        filtered_df["similarity"] +

        filtered_df["boost"]

    )

    # =========================
    # SORT
    # =========================

    results = (
        filtered_df
        .sort_values(
            by="final_score",
            ascending=False
        )
        .head(n_top)
    )

    final_results = []

    for _, row in results.iterrows():

        final_results.append({

            "name":
                row["name"],

            "genres":
                row["genres"],

            "tags":
                row["tags"],

            "year":
                int(row["year"]),

            "price":
                row["price"],

            "steam_price":
                row["price"],

            "similarity":
                round(
                    float(
                        row["similarity"]
                    ),
                    4
                ),

            "image_url":
                row["header_image"]
                if "header_image"
                in row
                else "",

            "steam_url":
                row["steamspy_url"]
                if "steamspy_url"
                in row
                else ""
        })

    return (
        final_results,
        rewritten_query
    )
