import requests
import streamlit as st


API_URL = "http://127.0.0.1:8001/query"


st.set_page_config(
    page_title="Game On",
    layout="wide"
)

st.title("🎮 Game On")

query = st.text_input(
    "Describe the game you are searching"
)

# -----------------------------
# FILTERS
# -----------------------------

st.sidebar.header("Filters")

genre = st.sidebar.text_input(
    "Genre",
    value="All"
)

content_type = st.sidebar.selectbox(
    "Content Type",
    ["all", "safe", "adult"]
)

min_price, max_price = st.sidebar.slider(
    "Price Range",
    0,
    100,
    (0, 50)
)

min_year, max_year = st.sidebar.slider(
    "Release Year",
    1990,
    2025,
    (2000, 2025)
)

# -----------------------------
# SEARCH
# -----------------------------

if st.button("Search Games"):

    with st.spinner("Searching games..."):

        response = requests.post(
            API_URL,
            json={
                "query": query,
                "genre": genre,
                "content_type": content_type,
                "min_price": min_price,
                "max_price": max_price,
                "min_year": min_year,
                "max_year": max_year
            }
        )

    st.write(f"Status code: {response.status_code}")

    if response.status_code == 200:

        data = response.json()

        rewritten_query = data["rewritten_query"]

        st.markdown("### 🧠 Rewritten Query")

        st.info(rewritten_query)

        results = data["results"]

        st.success(f"{len(results)} games found")

        for game in results:

            with st.container():

                st.markdown(f"## {game['name']}")

                st.markdown(
                    f"⭐ Similarity: {round(game['final_score'], 4)}"
                )

                st.markdown(
                    f"🎮 Genre: {game.get('genres', 'Unknown')}"
                )

                st.markdown(
                    f"🏷️ Tags: {game.get('tags', 'Unknown')}"
                )

                st.markdown(
                    f"📅 Year: {game.get('release_year', 'Unknown')}"
                )

                st.markdown(
                    f"💾 Dataset Price: ${game.get('price_num', 0)}"
                )

                steam_price = game.get("steam_price")

                if steam_price:
                    st.markdown(
                        f"💰 **Steam Price:** {steam_price}"
                    )

                steam_url = game.get("steam_url")

                if steam_url:
                    st.link_button(
                        "Steam Page",
                        steam_url
                    )

                st.divider()

    else:

        st.error("API Error")
        st.write(response.text)
