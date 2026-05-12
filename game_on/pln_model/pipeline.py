import os
import numpy as np

from pln_model.data import (
    load_data
)

from pln_model.limpieza import (
    limpieza
)

from pln_model.embeddings import (
    load_embedding_model,
    generate_embeddings
)

from pln_model.gcs import (
    download_embeddings_from_gcs,
    upload_embeddings_to_gcs
)

from pln_model.params import (

    EMBEDDINGS_PATH,

    GCS_BUCKET_NAME,

    GCS_EMBEDDINGS_BLOB_NAME
)


def load_pipeline():

    print("\nLoading dataset...\n")

    df = load_data()

    print("\nCleaning dataset...\n")

    df = limpieza(df)

    model = load_embedding_model()

    embeddings = None

    # =========================
    # LOCAL EMBEDDINGS
    # =========================

    if os.path.exists(
        EMBEDDINGS_PATH
    ):

        print(
            "\nLoading local embeddings...\n"
        )

        embeddings = np.load(
            EMBEDDINGS_PATH
        )

    else:

        # =========================
        # GCS DOWNLOAD
        # =========================

        try:

            print(
                "\nDownloading embeddings"
                " from GCS...\n"
            )

            download_embeddings_from_gcs(
                bucket_name=
                GCS_BUCKET_NAME,

                source_blob_name=
                GCS_EMBEDDINGS_BLOB_NAME,

                destination_file_name=
                EMBEDDINGS_PATH
            )

            embeddings = np.load(
                EMBEDDINGS_PATH
            )

        except Exception as e:

            print(
                "\nCould not download"
                " embeddings.\n"
            )

            print(e)

            # =========================
            # GENERATE EMBEDDINGS
            # =========================

            print(
                "\nGenerating embeddings...\n"
            )

            embeddings = generate_embeddings(
                texts=df[
                    "combined_text"
                ].tolist(),

                model=model,

                batch_size=128
            )

            os.makedirs(
                "embeddings",
                exist_ok=True
            )

            np.save(
                EMBEDDINGS_PATH,
                embeddings
            )

            # =========================
            # UPLOAD TO GCS
            # =========================

            try:

                upload_embeddings_to_gcs(
                    bucket_name=
                    GCS_BUCKET_NAME,

                    source_file_name=
                    EMBEDDINGS_PATH,

                    destination_blob_name=
                    GCS_EMBEDDINGS_BLOB_NAME
                )

            except Exception as upload_error:

                print(upload_error)

    return (
        df,
        embeddings,
        model
    )
