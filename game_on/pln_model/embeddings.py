import numpy as np

from sentence_transformers import SentenceTransformer

from tqdm import tqdm

from pln_model.params import (
    EMBEDDING_MODEL_NAME
)


def load_embedding_model():

    print(
        f"\nLoading model:"
        f" {EMBEDDING_MODEL_NAME}\n"
    )

    model = SentenceTransformer(
        EMBEDDING_MODEL_NAME
    )

    return model


def generate_embeddings(
    texts,
    model,
    batch_size=128
):

    embeddings = []

    for i in tqdm(
        range(0, len(texts), batch_size),
        desc="Generating embeddings"
    ):

        batch = texts[
            i:i + batch_size
        ]

        emb = model.encode(
            batch,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        embeddings.append(emb)

    embeddings = np.vstack(embeddings)

    return embeddings
