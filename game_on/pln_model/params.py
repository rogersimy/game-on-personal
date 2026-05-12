import os


# =========================
# EMBEDDINGS
# =========================

EMBEDDINGS_PATH = "embeddings/games.npy"

# =========================
# GCS
# =========================

GCS_BUCKET_NAME = "game_on_embeddings"

GCS_EMBEDDINGS_BLOB_NAME = "games.npy"

# =========================
# OPENAI / GROK
# =========================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

OPENAI_MODEL = "gpt-4.1-mini"

# =========================
# EMBEDDING MODEL
# =========================

EMBEDDING_MODEL_NAME = (
    "sentence-transformers/all-MiniLM-L6-v2"
)
