from openai import OpenAI
from pln_model.params import OPENAI_API_KEY


# =====================================================
# CLIENT
# =====================================================

client = None

if OPENAI_API_KEY:

    client = OpenAI(
        api_key=OPENAI_API_KEY
    )


# =====================================================
# QUERY REWRITER
# =====================================================

def rewrite_query(query):

    if not client:

        return query

    try:

        prompt = f"""
You are a video game search assistant.

Expand the following user query into a richer
semantic game search query.

Rules:
- Keep original meaning
- Add relevant gaming concepts
- Add gameplay genres
- Add likely mechanics
- Add thematic concepts
- Return ONLY the rewritten query
- Do not explain

User query:
{query}
"""

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3
        )

        rewritten = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return rewritten

    except Exception as e:

        print(e)

        return query
