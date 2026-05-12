from sentence_transformers import util
import torch
import numpy as np
import requests

from pln_model.query_rewriter import rewrite_query


# =====================================================
# TAGS
# =====================================================

ADULT_TAGS = [
    "nudity",
    "sexual",
    "hentai",
    "adult",
    "nsfw",
    "explicit"
]

KIDS_TAGS = [
    "kids",
    "family",
    "cartoon",
    "cute",
    "education"
]


# =====================================================
# CACHE
# =====================================================

STEAM_PRICE_CACHE = {}


# =====================================================
# STEAM API
# =====================================================

def get_steam_price(app_id):

    if app_id in STEAM_PRICE_CACHE:

        return STEAM_PRICE_CACHE[app_id]

    try:

        url = (
            "https://store.steampowered.com/api/appdetails"
            f"?appids={app_id}"
            "&cc=us"
        )

        response = requests.get(
            url,
            timeout=5
        )

        data = response.json()

        if not data[str(app_id)]["success"]:

            return None

        game_data = data[str(app_id)]["data"]

        if game_data.get("is_free"):

            result = {
                "steam_price": "Free",
                "discount_price": None,
                "discount_percent": 0
            }

            STEAM_PRICE_CACHE[app_id] = result

            return result

        price_data = game_data.get("price_overview")

        if not price_data:

            return None

        result = {
            "steam_price": price_data["initial"] / 100,
            "discount_price": price_data["final"] / 100,
            "discount_percent": price_data["discount_percent"]
        }

        STEAM_PRICE_CACHE[app_id] = result

        return result

    except Exception as e:

        print(f"Steam API Error: {e}")

        return None


# =====================================================
# FILTERS
# =====================================================

def apply_hard_filters(
    df,
    genre=None,
    content_type=None,
    min_price=0,
    max_price=999,
    min_year=1970,
    max_year=2030
):

    filtered_df = df.copy()

    # =================================================
    # PRICE
    # =================================================

    filtered_df = filtered_df[
        (
            filtered_df["original_price"] >= min_price
        ) &
        (
            filtered_df["original_price"] <= max_price
        )
    ]

    # =================================================
    # YEAR
    # =================================================

    filtered_df = filtered_df[
        (
            filtered_df["release_date"] >= min_year
        ) &
        (
            filtered_df["release_date"] <= max_year
        )
    ]

    # =================================================
    # GENRE
    # =================================================

    if genre and genre != "Any":

        filtered_df = filtered_df[
            filtered_df["genre"]
            .fillna("")
            .str.lower()
            .str.contains(
                genre.lower(),
                na=False
            )
        ]

    # =================================================
    # CONTENT TYPE
    # =================================================

    tags_series = (
        filtered_df["popular_tags"]
        .fillna("")
        .str.lower()
    )

    if content_type == "Adult":

        pattern = "|".join(ADULT_TAGS)

        filtered_df = filtered_df[
            tags_series.str.contains(
                pattern,
                regex=True,
                na=False
            )
        ]

    elif content_type == "Kids":

        pattern = "|".join(KIDS_TAGS)

        filtered_df = filtered_df[
            tags_series.str.contains(
                pattern,
                regex=True,
                na=False
            )
        ]

    elif content_type == "Safe":

        pattern = "|".join(ADULT_TAGS)

        filtered_df = filtered_df[
            ~tags_series.str.contains(
                pattern,
                regex=True,
                na=False
            )
        ]

    return filtered_df


# =====================================================
# QUERY
# =====================================================

def query_games(
    consulta,
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

    # =================================================
    # QUERY REWRITING
    # =================================================

    rewritten_query = rewrite_query(
        consulta
    )

    print("\n==========================")
    print("ORIGINAL QUERY:")
    print(consulta)

    print("\nREWRITTEN QUERY:")
    print(rewritten_query)
    print("==========================\n")

    # =================================================
    # FILTERS
    # =================================================

    filtered_df = apply_hard_filters(
        df=df,
        genre=genre,
        content_type=content_type,
        min_price=min_price,
        max_price=max_price,
        min_year=min_year,
        max_year=max_year
    )

    if len(filtered_df) == 0:

        return []

    # =================================================
    # EMBEDDINGS ALIGNMENT
    # =================================================

    filtered_indices = filtered_df.index.to_numpy()

    valid_mask = filtered_indices < len(embeddings)

    filtered_indices = filtered_indices[
        valid_mask
    ]

    filtered_df = filtered_df.iloc[
        valid_mask
    ]

    filtered_embeddings = embeddings[
        filtered_indices
    ]

    filtered_df = filtered_df.reset_index(
        drop=True
    )

    # =================================================
    # QUERY EMBEDDING
    # =================================================

    query_embedding = model.encode(
        rewritten_query,
        convert_to_tensor=True,
        normalize_embeddings=True
    )

    if isinstance(filtered_embeddings, np.ndarray):

        filtered_embeddings = torch.tensor(
            filtered_embeddings,
            dtype=torch.float32
        )

    cosine_scores = util.cos_sim(
        query_embedding,
        filtered_embeddings
    )[0]

    # =================================================
    # NAME BOOST
    # =================================================

    query_words = rewritten_query.lower().split()

    for idx, row in filtered_df.iterrows():

        game_name = str(
            row.get("name", "")
        ).lower()

        boost = 0

        for word in query_words:

            if word in game_name:

                boost += 0.08

        cosine_scores[idx] += boost

    # =================================================
    # TOP RESULTS
    # =================================================

    n_top = min(
        n_top,
        len(filtered_df)
    )

    top_results = torch.topk(
        cosine_scores,
        k=n_top
    )

    resultados = []

    for score, idx in zip(
        top_results.values,
        top_results.indices
    ):

        game = filtered_df.iloc[
            idx.item()
        ]

        url = game.get("url", "")

        image_url = None

        steam_price = None
        discount_price = None
        discount_percent = 0

        try:

            if "/app/" in url:

                app_id = (
                    url.split("/app/")[1]
                    .split("/")[0]
                )

                image_url = (
                    "https://cdn.cloudflare.steamstatic.com/"
                    f"steam/apps/{app_id}/capsule_616x353.jpg"
                )

                steam_data = get_steam_price(
                    app_id
                )

                if steam_data:

                    steam_price = steam_data["steam_price"]

                    discount_price = steam_data["discount_price"]

                    discount_percent = steam_data["discount_percent"]

        except Exception as e:

            print(e)

        resultados.append({

            "name": str(
                game.get("name", "")
            ),

            "score": float(
                round(score.item(), 4)
            ),

            "genre": str(
                game.get("genre", "")
            ),

            "tags": str(
                game.get("popular_tags", "")
            ),

            "price": float(
                game.get("original_price", 0)
            ),

            "steam_price": steam_price,

            "discount_price": discount_price,

            "discount_percent": int(
                discount_percent
            ),

            "year": int(
                game.get("release_date", 0)
            ),

            "url": str(url),

            "image_url": image_url,

            "rewritten_query": rewritten_query
        })

    return resultados
