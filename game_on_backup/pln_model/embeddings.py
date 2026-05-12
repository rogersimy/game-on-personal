from sentence_transformers import SentenceTransformer

_model_cache = {}


# =====================================================
# LOAD MODEL
# =====================================================

def get_model(
    model_name,
    device="cpu"
):

    global _model_cache

    key = f"{model_name}_{device}"

    if key not in _model_cache:

        print(f"\nLoading model: {model_name}\n")

        _model_cache[key] = SentenceTransformer(
            model_name,
            device=device
        )

    return _model_cache[key]


# =====================================================
# GENERATE EMBEDDINGS
# =====================================================

def generate_embeddings(
    texts,
    model_name,
    batch_size=256,
    device="cpu"
):

    model = get_model(
        model_name=model_name,
        device=device
    )

    print(
        f"\nGenerating embeddings for "
        f"{len(texts)} games\n"
    )

    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print("\nEmbeddings generated successfully")

    print(
        f"Embeddings shape: {embeddings.shape}"
    )

    return embeddings
