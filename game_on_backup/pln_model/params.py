from pathlib import Path
import os


# =====================================================
# ROOT
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# =====================================================
# DATA
# =====================================================

RAW_DATA_DIR = BASE_DIR / "raw_data"

CSV_PATH = RAW_DATA_DIR / "steam_games.csv"


# =====================================================
# EMBEDDINGS
# =====================================================

EMBEDDINGS_DIR = BASE_DIR / "embeddings"

EMBEDDINGS_DIR.mkdir(
    exist_ok=True
)

EMBEDDINGS_PATH = (
    EMBEDDINGS_DIR / "games.npy"
)


# =====================================================
# MODEL
# =====================================================

MODEL_NAME = "all-MiniLM-L6-v2"


# =====================================================
# GCS
# =====================================================

GCS_BUCKET = "game_on_embeddings"

GCS_EMBEDDINGS_FILE = "games.npy"


# =====================================================
# OPENAI
# =====================================================

OPENAI_API_KEY = os.getenv(
    "OPENAI_API_KEY"
)
