from fastapi import FastAPI
from pydantic import BaseModel

from pln_model.pipeline import load_pipeline

from pln_model.retrieval import query_games


# ---------------------------------------------------
# FASTAPI APP
# ---------------------------------------------------

app = FastAPI()


# ---------------------------------------------------
# LOAD MODEL + DATA
# ---------------------------------------------------

df, embeddings, model = load_pipeline()


# ---------------------------------------------------
# REQUEST MODEL
# ---------------------------------------------------

class QueryRequest(BaseModel):

    query: str

    genre: str | None = None

    content_type: str | None = None

    min_price: int = 0
    max_price: int = 999

    min_year: int = 1970
    max_year: int = 2030


# ---------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------

@app.get("/")
def root():

    return {
        "status": "ok",
        "message": "GAME ON API running"
    }


# ---------------------------------------------------
# QUERY ENDPOINT
# ---------------------------------------------------

@app.post("/query")
def recommend(request: QueryRequest):

    try:

        results, rewritten_query = query_games(
            query=request.query,
            df=df,
            embeddings=embeddings,
            model=model,
            n_top=8,
            genre=request.genre,
            content_type=request.content_type,
            min_price=request.min_price,
            max_price=request.max_price,
            min_year=request.min_year,
            max_year=request.max_year
        )

        return {

            # frontend expects this key
            "consulta_mejorada": rewritten_query,

            # frontend expects this key
            "recommendations": results,

            # optional assistant message
            "respuesta": (
                f"Found {len(results)} recommendations "
                f"for your search."
            )
        }

    except Exception as e:

        print("API ERROR:", str(e))

        return {
            "error": str(e)
        }
