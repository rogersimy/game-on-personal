import os
import numpy as np

from pln_model.params import *

from pln_model.data import load_raw_data

from pln_model.limpieza import limpieza

from pln_model.embeddings import (
    generate_embeddings,
    get_model
)

from pln_model.gcs import (
    download_embeddings_from_gcs,
    upload_embeddings_to_gcs
)


# =====================================================
# PIPELINE
# =====================================================

def load_pipeline():

    print("\nLoading dataset...\n")

    df = load_raw_data(
        CSV_PATH
    )

    print(
        f"Original dataset: {df.shape}"
    )

    # =================================================
    # CLEAN
    # =================================================

    df = limpieza(df)

    print(
        f"After cleaning: {df.shape}"
    )

    df = df.dropna(
        subset=["embedding"]
    )

    df = df.reset_index(
        drop=True
    )

    # =================================================
    # EMBEDDINGS
    # =================================================

    if not os.path.exists(
        EMBEDDINGS_PATH
    ):

        print(
            "\nDownloading embeddings from GCS...\n"
        )

        try:

            download_embeddings_from_gcs(
                bucket_name=GCS_BUCKET,
                source_blob_name=GCS_EMBEDDINGS_FILE,
                destination_file_name=EMBEDDINGS_PATH
            )

        except Exception as e:

            print(e)

            print(
                "\nGenerating embeddings locally...\n"
            )

            embeddings = generate_embeddings(
                texts=df["embedding"].tolist(),
                model_name=MODEL_NAME
            )

            np.save(
                EMBEDDINGS_PATH,
                embeddings
            )

            print(
                "\nUploading embeddings to GCS...\n"
            )

            upload_embeddings_to_gcs(
                bucket_name=GCS_BUCKET,
                source_file_name=EMBEDDINGS_PATH,
                destination_blob_name=GCS_EMBEDDINGS_FILE
            )

    print("\nLoading embeddings...\n")

    embeddings = np.load(
        EMBEDDINGS_PATH,
        allow_pickle=True
    )

    print(
        f"Embeddings shape: {embeddings.shape}"
    )

    # =================================================
    # ALIGNMENT
    # =================================================

    min_size = min(
        len(df),
        len(embeddings)
    )

    df = df.iloc[:min_size]

    embeddings = embeddings[:min_size]

    # =================================================
    # MODEL
    # =================================================

    model = get_model(
        MODEL_NAME
    )

    print(
        "\nPipeline loaded successfully\n"
    )

    return df, embeddings, model
