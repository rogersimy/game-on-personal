from fastapi import FastAPI
from pydantic import BaseModel

from pln_model.pipeline import load_pipeline
from pln_model.retrieval import query_games


# =====================================================
# LOAD PIPELINE
# =====================================================

df, embeddings, model = load_pipeline()


# =====================================================
# FASTAPI
# =====================================================

app = FastAPI(
    title="Game Recommendation API"
)


# =====================================================
# REQUEST MODEL
# =====================================================

class QueryRequest(BaseModel):

    query: str

    n_top: int = 5

    genre: str = "Any"

    content_type: str = "Any"

    min_price: float = 0

    max_price: float = 999

    min_year: int = 1970

    max_year: int = 2030


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home():

    return {
        "message": "Game Recommendation API Running"
    }


# =====================================================
# QUERY
# =====================================================

@app.post("/query")
def recommend(payload: QueryRequest):

    results = query_games(
        consulta=payload.query,
        df=df,
        embeddings=embeddings,
        model=model,
        n_top=payload.n_top,
        genre=payload.genre,
        content_type=payload.content_type,
        min_price=payload.min_price,
        max_price=payload.max_price,
        min_year=payload.min_year,
        max_year=payload.max_year
    )

    return {
        "recommendations": results
    }
