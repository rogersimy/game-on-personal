from google.cloud import storage
from pathlib import Path


# =====================================================
# DOWNLOAD
# =====================================================

def download_embeddings_from_gcs(
    bucket_name,
    source_blob_name,
    destination_file_name
):

    storage_client = storage.Client()

    bucket = storage_client.bucket(
        bucket_name
    )

    blob = bucket.blob(
        source_blob_name
    )

    if not blob.exists():

        raise FileNotFoundError(
            f"""
            File not found in GCS:

            bucket={bucket_name}
            file={source_blob_name}
            """
        )

    Path(
        destination_file_name
    ).parent.mkdir(
        parents=True,
        exist_ok=True
    )

    blob.download_to_filename(
        destination_file_name
    )

    print(
        f"\nDownloaded from GCS:\n"
        f"{source_blob_name}\n"
    )


# =====================================================
# UPLOAD
# =====================================================

def upload_embeddings_to_gcs(
    bucket_name,
    source_file_name,
    destination_blob_name
):

    storage_client = storage.Client()

    bucket = storage_client.bucket(
        bucket_name
    )

    blob = bucket.blob(
        destination_blob_name
    )

    blob.upload_from_filename(
        source_file_name
    )

    print(
        f"\nUploaded to GCS:\n"
        f"{destination_blob_name}\n"
    )
