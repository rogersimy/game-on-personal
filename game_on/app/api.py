from fastapi import FastAPI
from pydantic import BaseModel

from pln_model.pipeline import (
    load_pipeline
)

from pln_model.retrieval import (
    query_games
)


app = FastAPI()


df, embeddings, model = load_pipeline()


class QueryRequest(BaseModel):

    query: str

    genre: str | None = None

    content_type: str | None = None

    min_price: int = 0
    max_price: int = 999

    min_year: int = 1970
    max_year: int = 2030


@app.post("/query")
def recommend(request: QueryRequest):

    results, rewritten_query = query_games(
        query=request.query,
        df=df,
        embeddings=embeddings,
        model=model,
        n_top=5,
        genre=request.genre,
        content_type=request.content_type,
        min_price=request.min_price,
        max_price=request.max_price,
        min_year=request.min_year,
        max_year=request.max_year
    )

    return {
        "rewritten_query": rewritten_query,
        "results": results
    }
