from pathlib import Path
import json
import argparse
from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer


CHUNKS_PATH = Path("data/processed/chunks.jsonl")
CHROMA_DIR = Path("data/chroma_db")
COLLECTION_NAME = "wsu_survival_guide"

EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
DEFAULT_TOP_K = 4


EVAL_QUERIES = [
    "What should international students use myWSU for before or after arriving at WSU?",
    "What should international students do for SEVIS check-in after arriving at WSU?",
    "How can WSU students use Pullman Transit without paying a fare each time?",
    "What is the CougarCard used for at WSU?",
    "How can students find vegan, vegetarian, halal, or allergen-friendly food at WSU Dining?",
]


def load_chunks(path: Path) -> List[Dict[str, Any]]:
    """Load chunks created by scripts/ingest_and_chunk.py."""
    if not path.exists():
        raise FileNotFoundError(
            f"Could not find {path}. Run scripts/ingest_and_chunk.py first."
        )

    chunks = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            chunks.append(json.loads(line))

    if not chunks:
        raise ValueError(f"No chunks found in {path}.")

    return chunks


def get_chroma_collection(reset: bool = False):
    """
    Create or load a persistent ChromaDB collection.

    hnsw:space = cosine means lower distance is better.
    A distance close to 0 means very similar.
    """
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)

    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection: {COLLECTION_NAME}")
        except Exception:
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    return collection


def embed_and_store_chunks(chunks: List[Dict[str, Any]], reset: bool = True):
    """
    Embed all chunks and store them in ChromaDB with metadata.
    """
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)

    collection = get_chroma_collection(reset=reset)

    documents = []
    ids = []
    metadatas = []

    for chunk in chunks:
        chunk_id = chunk["chunk_id"]
        text = chunk["text"]
        metadata = chunk["metadata"]

        documents.append(text)
        ids.append(chunk_id)

        # Chroma metadata values should be simple types.
        metadatas.append(
            {
                "source_id": str(metadata.get("source_id", "")),
                "source_title": str(metadata.get("source_title", "")),
                "source_url": str(metadata.get("source_url", "")),
                "source_type": str(metadata.get("source_type", "")),
                "chunk_index": int(metadata.get("chunk_index", 0)),
            }
        )

    print(f"Embedding {len(documents)} chunks...")
    embeddings = model.encode(
        documents,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True,
    ).tolist()

    print("Adding chunks to ChromaDB...")
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print(f"Stored {collection.count()} chunks in ChromaDB.")
    return collection, model


def load_retriever():
    """
    Load the existing ChromaDB collection and embedding model.
    """
    print(f"Loading embedding model: {EMBEDDING_MODEL_NAME}")
    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    collection = get_chroma_collection(reset=False)

    if collection.count() == 0:
        raise ValueError(
            "ChromaDB collection is empty. Run with --build first."
        )

    return collection, model


def retrieve(query: str, collection, model, k: int = DEFAULT_TOP_K):
    """
    Retrieve top-k chunks for a query.
    """
    query_embedding = model.encode(
        [query],
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    retrieved = []

    for i in range(len(results["documents"][0])):
        retrieved.append(
            {
                "rank": i + 1,
                "text": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i],
            }
        )

    return retrieved


def print_results(query: str, results: List[Dict[str, Any]]):
    print("=" * 100)
    print(f"QUERY: {query}")
    print("=" * 100)

    for item in results:
        metadata = item["metadata"]

        print(f"\nRank {item['rank']}")
        print(f"Distance: {item['distance']:.4f}")
        print(f"Source: {metadata.get('source_title')}")
        print(f"Chunk index: {metadata.get('chunk_index')}")
        print(f"URL: {metadata.get('source_url')}")
        print("-" * 100)
        print(item["text"][:1000])
        print()


def run_evaluation(collection, model, k: int = DEFAULT_TOP_K):
    """
    Test retrieval on the evaluation-plan questions.
    Saves results to data/processed/retrieval_test_results.md.
    """
    out_path = Path("data/processed/retrieval_test_results.md")

    lines = []
    lines.append("# Milestone 4 Retrieval Test Results\n")
    lines.append(f"Embedding model: `{EMBEDDING_MODEL_NAME}`\n")
    lines.append(f"Vector store: `ChromaDB`\n")
    lines.append(f"Top-k: `{k}`\n")

    for query in EVAL_QUERIES:
        results = retrieve(query, collection, model, k=k)
        print_results(query, results)

        lines.append(f"\n## Query\n\n{query}\n")

        for item in results:
            metadata = item["metadata"]
            lines.append(f"\n### Rank {item['rank']}\n")
            lines.append(f"- Distance: `{item['distance']:.4f}`\n")
            lines.append(f"- Source: {metadata.get('source_title')}\n")
            lines.append(f"- Chunk index: {metadata.get('chunk_index')}\n")
            lines.append(f"- URL: {metadata.get('source_url')}\n")
            lines.append("\n```text\n")
            lines.append(item["text"][:1200])
            lines.append("\n```\n")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved retrieval test results to: {out_path}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build",
        action="store_true",
        help="Embed chunks and build/rebuild the ChromaDB collection.",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run retrieval tests using the evaluation questions.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Run retrieval for one custom query.",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=DEFAULT_TOP_K,
        help="Number of chunks to retrieve.",
    )

    args = parser.parse_args()

    if args.build:
        chunks = load_chunks(CHUNKS_PATH)
        collection, model = embed_and_store_chunks(chunks, reset=True)
    else:
        collection, model = load_retriever()

    if args.test:
        run_evaluation(collection, model, k=args.k)

    if args.query:
        results = retrieve(args.query, collection, model, k=args.k)
        print_results(args.query, results)

    if not args.test and not args.query:
        print("Done. Use --test or --query to test retrieval.")


if __name__ == "__main__":
    main()