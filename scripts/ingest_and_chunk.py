from pathlib import Path
import re
import json
import html
import requests
from bs4 import BeautifulSoup

SOURCES_FILE = Path("sources.md")

RAW_DIR = Path("data/raw_docs")
CLEAN_DIR = Path("data/clean_docs")
OUT_DIR = Path("data/processed")

CHUNK_SIZE = 900
CHUNK_OVERLAP = 200

RAW_DIR.mkdir(parents=True, exist_ok=True)
CLEAN_DIR.mkdir(parents=True, exist_ok=True)
OUT_DIR.mkdir(parents=True, exist_ok=True)


def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"https?://", "", text)
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")[:80]


def read_sources_from_markdown(path: Path):
    """
    Reads sources from sources.md in this format:

    ### 1. Source Title
    **URL:** https://...
    **Type:** Official WSU ...
    **Topics:** ...
    """
    text = path.read_text(encoding="utf-8")
    sources = []

    current_id = None
    current_title = None
    current_type = ""
    current_topics = ""

    for line in text.splitlines():
        line = line.strip()

        heading_match = re.match(r"^###\s+(\d+)\.\s+(.+)$", line)
        if heading_match:
            current_id = heading_match.group(1)
            current_title = heading_match.group(2).strip()
            current_type = ""
            current_topics = ""
            continue

        if line.startswith("**Type:**"):
            current_type = line.replace("**Type:**", "").strip()
            continue

        if line.startswith("**Topics:**"):
            current_topics = line.replace("**Topics:**", "").strip()
            continue

        url_match = re.match(r"^\*\*URL:\*\*\s+(https?://\S+)", line)
        if url_match and current_title:
            url = url_match.group(1).strip()

            source_type = (
                "unofficial student discussion"
                if "reddit.com" in url
                else "official WSU source"
            )

            sources.append(
                {
                    "id": current_id,
                    "title": current_title,
                    "description": current_topics,
                    "url": url,
                    "source_type": source_type,
                    "original_type": current_type,
                }
            )

    return sources


def fetch_url(url: str) -> str:
    """
    Downloads webpage HTML.

    Some websites, especially Reddit, may block requests or return limited content.
    If a clean .txt file already exists, the script will use that instead of overwriting it.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; AI201-RAG-Project/1.0)"
    }

    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return response.text


def html_to_text(html_content: str) -> str:
    """
    Converts HTML into readable plain text and removes common boilerplate.
    """
    soup = BeautifulSoup(html_content, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "form"]):
        tag.decompose()

    for tag_name in ["nav", "footer", "header", "aside"]:
        for tag in soup.find_all(tag_name):
            tag.decompose()

    text = soup.get_text(separator="\n")
    text = html.unescape(text)

    lines = []

    boilerplate_phrases = [
        "skip to content",
        "skip to site navigation",
        "share this",
        "cookie",
        "privacy policy",
        "terms of use",
        "all rights reserved",
        "read more",
        "menu",
        "search",
        "facebook",
        "twitter",
        "instagram",
        "linkedin",
        "youtube",
        "powered by wordpress",
        "lost your password",
        "wsu login",
    ]

    for line in text.splitlines():
        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if any(phrase in lower for phrase in boilerplate_phrases):
            continue

        # Skip tiny navigation artifacts.
        if len(line) <= 2:
            continue

        lines.append(line)

    cleaned = "\n".join(lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = re.sub(r"[ \t]+", " ", cleaned)

    return cleaned.strip()


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    """
    Splits text into overlapping character chunks.
    """
    if overlap >= chunk_size:
        raise ValueError("Overlap must be smaller than chunk size.")

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def main():
    sources = read_sources_from_markdown(SOURCES_FILE)

    if not sources:
        raise ValueError(
            "No sources found. Check that sources.md has headings like "
            "'### 1. Source Title' and URL lines like '**URL:** https://...'"
        )

    all_chunks = []
    metadata_records = []

    print(f"Found {len(sources)} sources.\n")

    for source in sources:
        title = source["title"]
        url = source["url"]
        slug = f"{source['id']}_{slugify(title)}"

        raw_path = RAW_DIR / f"{slug}.html"
        clean_path = CLEAN_DIR / f"{slug}.txt"

        print(f"Loading source {source['id']}: {title}")
        print(f"URL: {url}")

        # Important:
        # If you manually cleaned or pasted text into data/clean_docs,
        # this script will reuse that file and will NOT overwrite it.
        if clean_path.exists() and clean_path.read_text(encoding="utf-8").strip():
            print(f"  Using existing clean text: {clean_path}")
            clean_text = clean_path.read_text(encoding="utf-8")

        else:
            try:
                html_content = fetch_url(url)
            except Exception as e:
                print("  Could not fetch URL.")
                print(f"  Error: {e}")
                print(f"  Skipping this source for now.\n")
                continue

            raw_path.write_text(html_content, encoding="utf-8")

            clean_text = html_to_text(html_content)
            clean_path.write_text(clean_text, encoding="utf-8")

        chunks = chunk_text(clean_text)

        print(f"  Clean characters: {len(clean_text)}")
        print(f"  Chunks: {len(chunks)}")
        print(f"  Clean text saved to: {clean_path}")

        if raw_path.exists():
            print(f"  Raw HTML saved to: {raw_path}")

        print()

        metadata_records.append(
            {
                **source,
                "raw_path": str(raw_path) if raw_path.exists() else "",
                "clean_path": str(clean_path),
                "num_characters": len(clean_text),
                "num_chunks": len(chunks),
            }
        )

        for i, chunk in enumerate(chunks):
            all_chunks.append(
                {
                    "chunk_id": f"{slug}_chunk_{i}",
                    "text": chunk,
                    "metadata": {
                        "source_id": source["id"],
                        "source_title": title,
                        "source_url": url,
                        "source_type": source["source_type"],
                        "original_type": source.get("original_type", ""),
                        "topics": source.get("description", ""),
                        "chunk_index": i,
                    },
                }
            )

    chunks_path = OUT_DIR / "chunks.jsonl"
    metadata_path = OUT_DIR / "document_metadata.json"

    with chunks_path.open("w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    metadata_path.write_text(
        json.dumps(metadata_records, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print("=" * 80)
    print(f"Total sources successfully loaded: {len(metadata_records)}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Saved chunks to: {chunks_path}")
    print(f"Saved metadata to: {metadata_path}")
    print("=" * 80)

    print("\nSample chunks to inspect:\n")

    # Print first 5 chunks overall.
    for chunk in all_chunks[:5]:
        print("-" * 80)
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(f"Source: {chunk['metadata']['source_title']}")
        print(chunk["text"][:900])
        print()

    print("\nRepresentative chunk check:\n")

    # Print one chunk from each source, so inspection is easier.
    seen_sources = set()
    for chunk in all_chunks:
        source_title = chunk["metadata"]["source_title"]

        if source_title in seen_sources:
            continue

        seen_sources.add(source_title)

        print("-" * 80)
        print(f"Source: {source_title}")
        print(f"Chunk ID: {chunk['chunk_id']}")
        print(chunk["text"][:500])
        print()

        if len(seen_sources) >= 10:
            break


if __name__ == "__main__":
    main()