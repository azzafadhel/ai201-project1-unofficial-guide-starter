from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(PROJECT_ROOT))

from query import ask


EVALUATION_QUESTIONS = [
    {
        "question": "What should international students use myWSU for before or after arriving at WSU?",
        "expected": "Students use myWSU to manage important university tasks such as admission information, student account details, tuition and fees, class-related information, and other official WSU student services.",
    },
    {
        "question": "What should international students do for SEVIS check-in after arriving at WSU?",
        "expected": "International students should complete the required SEVIS check-in process after arriving at WSU as part of their international student arrival requirements.",
    },
    {
        "question": "How can WSU students use Pullman Transit without paying a fare each time?",
        "expected": "WSU students can ride Pullman Transit by showing or using their CougarCard/WSU student ID because bus access is supported through WSU transit services and student fees.",
    },
    {
        "question": "What is the CougarCard used for at WSU?",
        "expected": "The CougarCard is the WSU student ID and can be used for campus services such as dining/Cougar CASH, residence hall access, Student Recreation Center access, Pullman Transit, and other WSU services.",
    },
    {
        "question": "How can students find vegan, vegetarian, halal, or allergen-friendly food at WSU Dining?",
        "expected": "Students can use WSU Dining menu labels and NetNutrition to check ingredients, allergens, and dietary categories such as vegan, vegetarian, halal, gluten-friendly, and other food options.",
    },
]


OUT_OF_SCOPE_QUESTION = "What are the best hiking trails in Seattle?"


def format_sources(sources):
    if not sources:
        return "No sources returned."
    return "\n".join(f"- {source}" for source in sources)


def main():
    output_path = Path("data/processed/final_evaluation_report.md")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("# Final Evaluation Report\n")
    lines.append("This report records the system response for each evaluation question.\n")

    print("\nRunning evaluation questions...\n")

    for i, item in enumerate(EVALUATION_QUESTIONS, start=1):
        question = item["question"]
        expected = item["expected"]

        print("=" * 100)
        print(f"Question {i}: {question}")

        result = ask(question)
        answer = result["answer"]
        sources = result["sources"]

        print("\nAnswer:")
        print(answer)
        print("\nSources:")
        print(format_sources(sources))

        judgment = input("\nAccuracy judgment? Type accurate / partially accurate / inaccurate: ").strip()

        lines.append(f"\n## Question {i}\n")
        lines.append(f"**Question:** {question}\n")
        lines.append(f"**Expected answer:** {expected}\n")
        lines.append(f"**System response:** {answer}\n")
        lines.append(f"**Accuracy judgment:** {judgment}\n")
        lines.append("**Sources returned:**\n")
        lines.append(format_sources(sources))
        lines.append("\n")

    print("=" * 100)
    print("Out-of-scope test")
    print(f"Question: {OUT_OF_SCOPE_QUESTION}")

    result = ask(OUT_OF_SCOPE_QUESTION)
    answer = result["answer"]
    sources = result["sources"]

    print("\nAnswer:")
    print(answer)
    print("\nSources:")
    print(format_sources(sources))

    lines.append("\n## Out-of-Scope Test\n")
    lines.append(f"**Question:** {OUT_OF_SCOPE_QUESTION}\n")
    lines.append('**Expected behavior:** The system should say "I don\'t have enough information on that."\n')
    lines.append(f"**System response:** {answer}\n")
    lines.append("**Sources returned:**\n")
    lines.append(format_sources(sources))
    lines.append("\n")

    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nSaved evaluation report to: {output_path}")


if __name__ == "__main__":
    main()