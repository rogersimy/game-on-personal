import streamlit as st
import requests


API_URL = "http://127.0.0.1:8001/query"


# =====================================================
# PAGE
# =====================================================

st.set_page_config(
    page_title="Game-On",
    layout="wide"
)

st.title("🎮 Game On")


# =====================================================
# QUERY
# =====================================================

query = st.text_input(
    "Describe the game you are searching",
    "dungeon and dragons"
)


# =====================================================
# SIDEBAR
# =====================================================

st.sidebar.title("Filters")

genre = st.sidebar.selectbox(
    "Genre",
    [
        "Any",
        "Action",
        "Adventure",
        "RPG",
        "Strategy",
        "Simulation",
        "Indie",
        "Sports",
        "Racing"
    ]
)

content_type = st.sidebar.selectbox(
    "Content Type",
    [
        "Any",
        "Safe",
        "Adult",
        "Kids"
    ]
)

price_range = st.sidebar.slider(
    "Price Range",
    0.0,
    100.0,
    (0.0, 40.0)
)

year_range = st.sidebar.slider(
    "Release Year",
    1980,
    2026,
    (2010, 2026)
)

n_top = st.sidebar.slider(
    "Results",
    1,
    20,
    5
)


# =====================================================
# SEARCH
# =====================================================

if st.button("Search Games"):

    with st.spinner("Searching games..."):

        response = requests.post(
            API_URL,
            json={
                "query": query,
                "n_top": n_top,
                "genre": genre,
                "content_type": content_type,
                "min_price": price_range[0],
                "max_price": price_range[1],
                "min_year": year_range[0],
                "max_year": year_range[1]
            },
            timeout=120
        )

    st.write(
        "Status code:",
        response.status_code
    )

    if response.status_code != 200:

        st.error("API Error")

        st.code(response.text)

        st.stop()

    data = response.json()

    recommendations = data.get(
        "recommendations",
        []
    )

    if len(recommendations) == 0:

        st.warning("No games found")

        st.stop()

    # =================================================
    # REWRITTEN QUERY
    # =================================================

    st.subheader("🧠 Rewritten Query")

    st.info(
        recommendations[0].get(
            "rewritten_query",
            query
        )
    )

    st.success(
        f"{len(recommendations)} games found"
    )

    # =================================================
    # RESULTS
    # =================================================

    for game in recommendations:

        st.divider()

        col1, col2 = st.columns(
            [1, 3]
        )

        # =============================================
        # IMAGE
        # =============================================

        with col1:

            image_url = game.get(
                "image_url"
            )

            if image_url:

                st.image(
                    image_url,
                    width="stretch"
                )

        # =============================================
        # INFO
        # =============================================

        with col2:

            st.subheader(
                game.get("name")
            )

            st.write(
                f"⭐ Similarity: {game.get('score')}"
            )

            st.write(
                f"🎮 Genre: {game.get('genre')}"
            )

            st.write(
                f"🏷️ Tags: {game.get('tags')}"
            )

            st.write(
                f"📅 Year: {game.get('year')}"
            )

            st.write(
                f"💾 Dataset Price: ${game.get('price')}"
            )

            # =========================================
            # STEAM PRICE
            # =========================================

            if game.get("steam_price") == "Free":

                st.success(
                    "🟢 Free to Play"
                )

            elif game.get("steam_price") is not None:

                if game.get(
                    "discount_percent",
                    0
                ) > 0:

                    st.error(
                        f"🔥 Steam Discount: "
                        f"${game.get('discount_price')} "
                        f"(-{game.get('discount_percent')}%)"
                    )

                    st.caption(
                        f"Original: "
                        f"${game.get('steam_price')}"
                    )

                else:

                    st.info(
                        f"💰 Steam Price: "
                        f"${game.get('steam_price')}"
                    )

            url = game.get("url")

            if url:

                st.link_button(
                    "Steam Page",
                    url
                )
