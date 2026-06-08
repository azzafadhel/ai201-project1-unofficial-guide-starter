# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->
I chose WSU Campus Survival Guide for New and International Students.

This guide focuses on practical student knowledge for new and international students arriving at Washington State University in Pullman. The guide covers arrival tasks, transportation, dining, CougarCard use, banking, health resources, safety, winter preparation, and campus adjustment.

This knowledge is valuable because official WSU information is spread across many different department websites, including International Programs, Transportation Services, Dining Services, CougarCard, and campus life pages. Students often need one clear answer that combines the most relevant information. Some practical advice is also hard to find in official channels because it comes from student experience, such as whether students really need a car in Pullman, how useful the bus system is, and how weather affects getting around.
This domain is a good fit for a RAG system because answers should be grounded in actual WSU sources and student discussions instead of being guessed by the model.

---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | WSU International Student Handbook | Official WSU handbook covering housing, dining, transportation, health, banking, safety, academic support, cultural adjustment, winter clothing, and student life. | https://ip.wsu.edu/student-handbook/ |
| 2 | WSU Campus Arrival Guide | Official arrival guide for international students covering myWSU, WSU email, CougarCard, SEVIS check-in, banking, tuition, and orientation. | https://ip.wsu.edu/future-students/admitted-students/campus-arrival-guide/ |
| 3 | WSU New Student Checklist | Official checklist covering myWSU, WSU email, transfer credits, travel preparation, I-20, visa, packing, and SIM card options. | https://ip.wsu.edu/future-students/admitted-students/new-student-checklist/ |
| 4 | WSU Pullman Transportation | Official WSU Pullman transportation page covering Pullman Transit, buses, shuttle vans, biking, parking, ride-sharing, and campus access. | https://pullman.wsu.edu/community-life/transportation/ |
| 5 | WSU Transit Fee Information | Official WSU Transportation Services page explaining CougarCard bus access, student transit fees, Pullman Transit, and year-round service. | https://transportation.wsu.edu/transitfeeinformation/ |
| 6 | WSU Transit Options | Official WSU Transportation Services page about bus routes, schedules, transit apps, campus transportation, and commuting without a car. | https://transportation.wsu.edu/transportation-options/transit-options/ |
| 7 | WSU CougarCard Center | Official CougarCard page explaining the card as a student ID and campus service card for dining, Cougar CASH, residence halls, recreation, Pullman Transit, and campus services. | https://cougarcash.wsu.edu/home/ |
| 8 | WSU Dining Centers / Northside Café | Official WSU Dining page showing dining center information, campus food options, and dietary labels such as gluten-friendly, vegetarian, halal, and vegan. | https://dining.wsu.edu/dining-options/dining-centers/northside-cafe/ |
| 9 | WSU Dining Services Allergen and Dietary Information | Official WSU Dining nutrition page explaining NetNutrition, allergens, dietary restrictions, halal food, vegetarian food, vegan food, and ingredient search tools. | https://dining.wsu.edu/nutrition/navigation-netnutrition/ |
| 10 | Reddit Discussion: Do I Need a Car at WSU? | Unofficial student discussion about whether students need a car in Pullman, including buses, CougarCard, walking, biking, hills, winter weather, and student experience. | https://www.reddit.com/r/wsu/comments/1alaw7h/do_i_need_a_car/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**
900 characters per chunk.


**Overlap:**
200 characters.


**Reasoning:**
Most of the documents are structured as official web pages with headings and short sections. The WSU International Student Handbook is longer and covers many topics, while the arrival guide, checklist, transportation pages, CougarCard page, and dining pages are more focused. A chunk size of 900 characters should usually keep one complete topic together, such as CougarCard uses, transportation options, arrival steps, or dining allergy information.

The 200-character overlap helps avoid splitting important details across chunk boundaries. This is useful because many pages have a heading followed by several short paragraphs or bullet points. For example, a heading such as “CougarCard” or “Transportation” should stay close to the explanation that follows it.

For Reddit discussion content, each comment or small group of related comments should be treated as a chunk when possible. Reddit chunks should be marked as unofficial student perspective in metadata.
Each chunk will store metadata:source title, source URL or local file path, source type: official WSU source or unofficial student discussion, topic, if known, chunk index, ingestion date



For Milestone 3, I kept character-based chunking because the total chunk count was reasonable and the inspected chunks were mostly readable and useful. The script produced 189 chunks across 10 sources, which is within the expected range. I may improve this later with paragraph-aware chunking as a stretch improvement.



**Milestone 3 inspection result:**
After running `scripts/ingest_and_chunk.py`, the pipeline successfully loaded 10 sources and produced 189 total chunks. I inspected representative chunks from the WSU International Student Handbook, Campus Arrival Guide, Pullman Transportation page, CougarCard page, Dining pages, and Reddit discussion. The chunks contained useful student survival information such as housing, dining, transportation, CougarCard use, SEVIS check-in, myWSU, health resources, winter preparation, and student transportation advice.
---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**
sentence-transformers/all-MiniLM-L6-v2
**Top-k:**
Retrieve the top 4 chunks per query.
**Production tradeoff reflection:**
For this project, all-MiniLM-L6-v2 is a good embedding model because it is lightweight, fast, free to run locally, and works well for short practical questions.

If this system were deployed for real WSU students, I would compare stronger embedding models with better retrieval accuracy, longer context support, and stronger handling of informal language. This matters because the corpus mixes official WSU pages with informal Reddit student discussion. The main tradeoffs would be:

Accuracy: Larger embedding models may retrieve better results for vague student questions.
Latency: Larger models may be slower.
Cost: Hosted embedding APIs may cost money.
Context length: Longer context may help with the long international student handbook.
Source reliability: Official WSU sources should be preferred for factual answers, while Reddit should be used only for student experience.

The system should prioritize official WSU sources when answering factual questions. Reddit chunks should only be used when the question asks about student opinions or practical lived experience.
---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->


| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What should international students use myWSU for before or after arriving at WSU? | Students use myWSU to manage important university tasks such as admission information, student account details, tuition and fees, class-related information, and other official WSU student services. |
| 2 | What should international students do for SEVIS check-in after arriving at WSU? | International students should complete the required SEVIS check-in process after arriving at WSU as part of their international student arrival requirements. |
| 3 | How can WSU students use Pullman Transit without paying a fare each time? | WSU students can ride Pullman Transit by showing or using their CougarCard/WSU student ID because bus access is supported through WSU transit services and student fees. |
| 4 | What is the CougarCard used for at WSU? | The CougarCard is the WSU student ID and can be used for campus services such as dining/Cougar CASH, residence hall access, Student Recreation Center access, Pullman Transit, and other WSU services. |
| 5 | How can students find vegan, vegetarian, halal, or allergen-friendly food at WSU Dining? | Students can use WSU Dining menu labels and NetNutrition to check ingredients, allergens, and dietary categories such as vegan, vegetarian, halal, gluten-friendly, and other food options. |


---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.Official information may change over time.
Transportation schedules, dining hours, arrival steps, tuition deadlines, and campus service details may change by semester or academic year. To reduce this risk, the system should store source URLs and ingestion dates in metadata. For time-sensitive questions, the answer should mention that students should verify the official page.

2.The corpus mixes official and unofficial sources.
Official WSU pages are better for factual information, while Reddit is useful for student experience. The system must avoid treating Reddit opinions as official policy. Retrieval metadata should clearly label Reddit as unofficial student discussion.
The International Student Handbook is broad.

3.The handbook covers many topics in one long source. Poor chunking could mix unrelated information, such as banking, health, transportation, and winter clothing. The chunking process should preserve section headings when possible.
Some questions may require multiple sources.

4.A question like “Do I need a car at WSU?” may need both official transportation information and unofficial student experience. The retriever should return multiple chunks so the generator can combine official facts with student perspective.

5.Some chunks may start or end in the middle of a sentence.
Because the current implementation uses character-based chunking, a few chunks may have imperfect boundaries. I inspected sample chunks and decided this was acceptable for Milestone 3 because the chunks were still readable and substantive. A future improvement would be paragraph-aware chunking.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->



My system will start from the source URLs listed in `sources.md`. It will download each page, clean the text, split it into chunks, store the chunks in a vector database, then retrieve the most relevant chunks to answer student questions.



```text
Document Ingestion
URLs + requests + BeautifulSoup
        |
        v
Chunking
900 characters + 200 overlap
        |
        v
Embedding + Vector Store
all-MiniLM-L6-v2 + ChromaDB
        |
        v
Retrieval
top-k = 4
        |
        v
Generation
Groq API + Llama

Document Ingestion: Load the WSU and Reddit pages directly from their URLs.
Chunking: Split cleaned webpage text into overlapping chunks.
Embedding + Vector Store: Embed chunks using all-MiniLM-L6-v2 and store them in ChromaDB.
Retrieval: Retrieve the top 4 chunks most related to the user question.
Generation: Use Groq/Llama to answer using only the retrieved chunks.


---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->



**Milestone 3 — Ingestion and chunking:**

I will use ChatGPT, Claude, or GitHub Copilot to help implement the ingestion and chunking stage.

Input I will give the AI tool:

- The Documents section
- The Chunking Strategy section
- The source URLs from `sources.md`
- The requirement to fetch webpages using `requests` and `BeautifulSoup`
- The requirement to preserve metadata
- The requirement to label official WSU sources and Reddit differently

Expected output:

- A Python script that reads the URLs from `sources.md`
- Code that downloads each webpage using `requests`
- Code that cleans webpage text using `BeautifulSoup`
- A `chunk_text()` function with 900-character chunks and 200-character overlap
- A list of chunk dictionaries containing text and metadata

How I will verify the output:

- Confirm all 10 URLs are loaded
- Print the number of chunks per source
- Manually inspect chunks from the long handbook
- Confirm each chunk has source title, URL, source type, and chunk index
- Confirm Reddit chunks are labeled as unofficial student discussion


**Milestone 4 — Embedding and retrieval:**


I will use ChatGPT, Claude, or GitHub Copilot to help implement the embedding and retrieval code.

Input I will give the AI tool:

The Retrieval Approach section
The chunk dictionary format from Milestone 3
The requirement to use sentence-transformers/all-MiniLM-L6-v2
The requirement to use ChromaDB
The top-k value of 4

Expected output:

Code to initialize the embedding model
Code to create or load a ChromaDB collection
Code to add chunk text, metadata, and IDs to the vector store
A retrieve(query, k=4) function

How I will verify the output:

Ask the five evaluation questions
Print retrieved chunks before generation
Confirm transportation questions retrieve transportation sources
Confirm CougarCard questions retrieve the CougarCard source
Confirm dining restriction questions retrieve Dining or NetNutrition sources
Confirm unofficial Reddit chunks are not used as official policy


**Milestone 5 — Generation and interface:**
I will use ChatGPT, Claude, or GitHub Copilot to help implement the generation and user interface.

Input I will give the AI tool:

The Architecture section
The Retrieval Approach section
The Evaluation Plan
The requirement to answer only from retrieved context
The requirement to include source attribution

Expected output:

A function that formats retrieved chunks into context
A prompt template that tells the model to answer only from the context
Code that calls the Groq API or selected LLM
A simple command-line interface where users can ask questions
An answer format that includes sources

How I will verify the output:

Run all five evaluation questions
Compare generated answers to the expected answers
Check that the answer cites the correct source
Check that the model says it does not know when the answer is not in the retrieved context
Save evaluation results in a small notes file or table