from openai import OpenAI

from pln_model.params import (
    OPENAI_API_KEY,
    OPENAI_MODEL
)


client = None

if OPENAI_API_KEY:

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )


def rewrite_query(query):

    """
    Uses OpenAI/Grok-style query expansion
    to enrich semantic search.
    """

    if client is None:

        print(
            "\nNo OPENAI_API_KEY found."
            "\nUsing raw query.\n"
        )

        return query

    try:

        prompt = f"""
You are a video game search assistant.

Expand the following user query into a richer
semantic video game search query.

Rules:
- Keep original meaning
- Add relevant gaming concepts
- Add gameplay genres
- Add likely mechanics
- Add thematic concepts
- Add synonyms
- Return ONLY the rewritten query
- Do not explain

User query:
{query}
"""

        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        rewritten_query = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        print("\nREWRITTEN QUERY:")
        print(rewritten_query)
        print()

        return rewritten_query

    except Exception as e:

        print(f"\nQuery rewrite error: {e}\n")

        return query
