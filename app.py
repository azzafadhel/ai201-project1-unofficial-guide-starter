import gradio as gr
from query import ask


def handle_query(question):
    result = ask(question)

    answer = result["answer"]
    sources = "\n".join(f"• {source}" for source in result["sources"])

    retrieved_preview_lines = []
    for item in result["retrieved_chunks"]:
        metadata = item["metadata"]
        retrieved_preview_lines.append(
            f"Rank {item['rank']} | Distance: {item['distance']:.4f}\n"
            f"Source: {metadata.get('source_title')}\n"
            f"Chunk index: {metadata.get('chunk_index')}\n"
            f"{item['text'][:500]}..."
        )

    retrieved_preview = "\n\n---\n\n".join(retrieved_preview_lines)

    return answer, sources, retrieved_preview


with gr.Blocks(title="WSU Campus Survival Guide") as demo:
    gr.Markdown("# WSU Campus Survival Guide")
    gr.Markdown(
        "Ask a question about WSU arrival, transportation, CougarCard, dining, "
        "health resources, safety, winter preparation, or campus adjustment."
    )

    question = gr.Textbox(
        label="Your question",
        placeholder="Example: How can WSU students ride Pullman Transit?",
        lines=2,
    )

    ask_button = gr.Button("Ask")

    answer = gr.Textbox(label="Answer", lines=8)
    sources = gr.Textbox(label="Retrieved from", lines=5)
    retrieved_chunks = gr.Textbox(label="Retrieved chunk preview", lines=12)

    ask_button.click(
        handle_query,
        inputs=question,
        outputs=[answer, sources, retrieved_chunks],
    )

    question.submit(
        handle_query,
        inputs=question,
        outputs=[answer, sources, retrieved_chunks],
    )

    gr.Examples(
        examples=[
            "What should international students use myWSU for?",
            "What should international students do for SEVIS check-in?",
            "How can WSU students ride Pullman Transit?",
            "What is the CougarCard used for?",
            "How can students find vegan, halal, or allergen-friendly food?",
            "What are the best hiking trails in Seattle?",
        ],
        inputs=question,
    )


if __name__ == "__main__":
    demo.launch()