from pathlib import Path
from typing import Dict, Any, List

from dotenv import load_dotenv
from groq import Groq

from scripts.embed_and_retrieve import load_retriever, retrieve


MODEL_NAME = "llama-3.3-70b-versatile"
TOP_K = 4
MAX_DISTANCE = 0.75

load_dotenv()

collection, embedding_model = load_retriever()
client = Groq()


SYSTEM_PROMPT = """
You are a grounded RAG assistant for a WSU Campus Survival Guide.

Rules:
1. Answer using ONLY the provided retrieved context.
2. Do NOT use outside knowledge.
3. If the context does not contain enough information, say exactly:
   "I don't have enough information on that."
4. Be concise and helpful.
5. Do not invent policies, dates, locations, phone numbers, or links.
"""


def format_context(results: List[Dict[str, Any]]) -> str:
    context_blocks = []

    for i, item in enumerate(results, start=1):
        metadata = item["metadata"]
        context_blocks.append(
            f"[Source {i}]\n"
            f"Title: {metadata.get('source_title', 'Unknown')}\n"
            f"URL: {metadata.get('source_url', '')}\n"
            f"Chunk index: {metadata.get('chunk_index', '')}\n"
            f"Text:\n{item['text']}"
        )

    return "\n\n---\n\n".join(context_blocks)


def unique_sources(results: List[Dict[str, Any]]) -> List[str]:
    seen = set()
    sources = []

    for item in results:
        metadata = item["metadata"]
        title = metadata.get("source_title", "Unknown source")
        url = metadata.get("source_url", "")
        distance = item.get("distance", None)

        key = (title, url)
        if key in seen:
            continue

        seen.add(key)

        if distance is not None:
            sources.append(f"{title} — {url} (distance: {distance:.4f})")
        else:
            sources.append(f"{title} — {url}")

    return sources


def ask(question: str) -> Dict[str, Any]:
    question = question.strip()

    if not question:
        return {
            "answer": "Please enter a question.",
            "sources": [],
            "retrieved_chunks": [],
        }

    results = retrieve(question, collection, embedding_model, k=TOP_K)

    # If even the best retrieved chunk is weak, refuse before calling the LLM.
    if not results or results[0]["distance"] > MAX_DISTANCE:
        return {
            "answer": "I don't have enough information on that.",
            "sources": unique_sources(results),
            "retrieved_chunks": results,
        }

    context = format_context(results)

    user_prompt = f"""
Retrieved context:
{context}

Question:
{question}

Answer the question using only the retrieved context.
If the context does not contain the answer, say:
"I don't have enough information on that."
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=500,
    )

    answer = response.choices[0].message.content.strip()

    return {
        "answer": answer,
        "sources": unique_sources(results),
        "retrieved_chunks": results,
    }


if __name__ == "__main__":
    while True:
        q = input("\nAsk a question, or type 'exit': ").strip()
        if q.lower() in {"exit", "quit"}:
            break

        result = ask(q)
        print("\nAnswer:")
        print(result["answer"])

        print("\nSources:")
        for source in result["sources"]:
            print(f"- {source}")