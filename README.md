# The Unofficial Guide — Project 1

## Domain

My system covers a **WSU Campus Survival Guide for New and International Students**.

The guide focuses on practical student knowledge about arriving at Washington State University in Pullman, using myWSU, completing SEVIS check-in, getting around Pullman, using the CougarCard, finding dining options, handling dietary restrictions, preparing for winter, and adjusting to campus life.

This knowledge is valuable because it is spread across many different WSU pages, including International Programs, Transportation Services, Dining Services, CougarCard, and campus life pages. New students often need one clear answer instead of searching through many different official websites. Some practical information is also easier to understand through student discussions, such as whether students really need a car in Pullman.

---

## Document Sources

| #  | Source                                               | Type                                            | URL or file path                                                            |
| -- | ---------------------------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------------- |
| 1  | WSU International Student Handbook                   | Official WSU student handbook                   | https://ip.wsu.edu/student-handbook/                                        |
| 2  | WSU Campus Arrival Guide                             | Official WSU international student arrival page | https://ip.wsu.edu/future-students/admitted-students/campus-arrival-guide/  |
| 3  | WSU New Student Checklist                            | Official WSU international student checklist    | https://ip.wsu.edu/future-students/admitted-students/new-student-checklist/ |
| 4  | WSU Pullman Transportation                           | Official WSU Pullman transportation page        | https://pullman.wsu.edu/community-life/transportation/                      |
| 5  | WSU Transit Fee Information                          | Official WSU Transportation Services page       | https://transportation.wsu.edu/transitfeeinformation/                       |
| 6  | WSU Transit Options                                  | Official WSU Transportation Services page       | https://transportation.wsu.edu/transportation-options/transit-options/      |
| 7  | WSU CougarCard Center                                | Official CougarCard page                        | https://cougarcash.wsu.edu/home/                                            |
| 8  | WSU Dining Centers / Northside Café                  | Official WSU Dining page                        | https://dining.wsu.edu/dining-options/dining-centers/northside-cafe/        |
| 9  | WSU Dining Services Allergen and Dietary Information | Official WSU Dining nutrition page              | https://dining.wsu.edu/nutrition/navigation-netnutrition/                   |
| 10 | Reddit Discussion: Do I Need a Car at WSU?           | Unofficial student discussion                   | https://www.reddit.com/r/wsu/comments/1alaw7h/do_i_need_a_car/              |

The corpus includes mostly official WSU sources, plus one unofficial Reddit thread to capture student perspective about transportation and whether a car is needed in Pullman.

---

## Chunking Strategy

**Chunk size:**
900 characters per chunk.

**Overlap:**
200 characters.

**Why these choices fit your documents:**
Most of my documents are webpage-style resources with headings, short paragraphs, and bullet-like sections. A 900-character chunk is large enough to keep a complete idea together, such as CougarCard uses, SEVIS check-in instructions, transit information, or dining allergy guidance. A 200-character overlap helps preserve context when an important sentence or heading appears near a chunk boundary.

Before chunking, I cleaned the documents by removing HTML tags, scripts, style content, repeated navigation text, footer/header elements, and obvious boilerplate. Two sources needed manual cleanup: the WSU International Student Handbook and the Reddit discussion, because the original scraping results did not capture useful content.

For Milestone 3, I kept character-based chunking because the total chunk count was reasonable and the inspected chunks were mostly readable and useful. Some chunks start or end in the middle of a word or sentence, but the content was still substantive enough for retrieval. A future improvement would be paragraph-aware chunking.

**Final chunk count:**
189 chunks across 10 sources.

---

## Sample Chunks

### Sample Chunk 1 — WSU Campus Arrival Guide

Source: `WSU Campus Arrival Guide`

```text
myWSU
Your myWSU account is the central location where you will see your class schedule, pay your tuition, and many more important matters.
Log in to your myWSU account
WSU email
We know there are many forms of communication in the world. However, at WSU, your WSU email account is the ONLY way to communicate with important offices on campus, such as Housing, Bursar’s Office, professors, and more.
```

### Sample Chunk 2 — WSU Campus Arrival Guide

Source: `WSU Campus Arrival Guide`

```text
New Student SEVIS check-in
You are required to check in with SEVIS as a new student within your first week of being on campus. Failure to do so will result in the termination of your SEVIS record and could have a negative impact on your immigration status. Log in to myPassport using your WSU username and password and complete the new student check-in.
```

### Sample Chunk 3 — WSU Transit Fee Information

Source: `WSU Transit Fee Information`

```text
Students rely on transit. Pullman Transit provides as many as 1.4 million rides per year and most of those riders are WSU students!
Students need to simply show their CougarCard to ride the bus!
Pullman Transit provides services Monday through Sunday year-round.
```

### Sample Chunk 4 — WSU CougarCard Center

Source: `WSU CougarCard Center`

```text
Your CougarCard is the only card you need as a student at WSU. It serves as your university ID, lets you access facilities, pay for food, and so much more!
You'll need it for:
General university identification
Library privileges
Resident Meal Plan purchases
Cougar CASH purchases
Student Recreation Center access and rentals
Riding the Pullman Transit buses
Access to selected residence halls, campus offices, and buildings
```

### Sample Chunk 5 — WSU Dining Services Allergen and Dietary Information

Source: `WSU Dining Services Allergen and Dietary Information`

```text
What is NetNutrition?
You can use NetNutrition to view nutritional content and ingredients of your food choices, filter out foods based on traits, and select preferences for specific types of diets like vegan or Halal.
How to Use NetNutrition to Manage Your Food Allergy:
Find food allergens/intolerances listed on the left side of the page. Check the box next to the food allergens/intolerances you must avoid.
```

---

## Embedding Model

**Model used:**
`sentence-transformers/all-MiniLM-L6-v2`

I chose this model because it is lightweight, runs locally, does not require an API key, and is fast enough for a small class project. It works well for short practical questions like “What is myWSU used for?” or “How can students ride Pullman Transit?”

**Production tradeoff reflection:**
If I were deploying this for real students, I would compare larger embedding models with stronger semantic retrieval accuracy. I would consider context length, latency, cost, and whether the model handles informal student language well. Since my corpus includes both official WSU pages and one Reddit discussion, I would also care about robustness to both formal policy language and informal student wording. A larger API-hosted embedding model might improve retrieval, but it would increase cost and latency compared with a local sentence-transformers model.

---

## Embedding and Vector Store

I stored all chunks in **ChromaDB** using cosine distance. Each chunk was stored with metadata, including:

* source ID
* source title
* source URL
* source type
* chunk index

This metadata is important because the generation system later uses it to show source attribution.

The retrieval function accepts a user query, embeds it with `all-MiniLM-L6-v2`, and retrieves the top 4 most relevant chunks from ChromaDB.

---

## Retrieval Test Results

I tested retrieval with all 5 evaluation questions from `planning.md`. The system returned relevant chunks for each question, and the top retrieved result for each question had a distance below 0.5.

### Retrieval Test 1

**Query:**
What should international students use myWSU for before or after arriving at WSU?

**Top returned chunk:**
Source: WSU Campus Arrival Guide, chunk index 2, distance 0.3697.


myWSU
Your myWSU account is the central location where you will see your class schedule, pay your tuition, and many more important matters.
Log in to your myWSU account


**Why it is relevant:**
The returned chunk directly says that myWSU is used to see class schedules, pay tuition, and manage important student matters.

### Retrieval Test 2

**Query:**
What should international students do for SEVIS check-in after arriving at WSU?

**Top returned chunk:**
Source: WSU Campus Arrival Guide, chunk index 4, distance 0.3619.

```text
New Student SEVIS check-in
You are required to check in with SEVIS as a new student within your first week of being on campus. Failure to do so will result in the termination of your SEVIS record and could have a negative impact on your immigration status. Log in to myPassport using your WSU username and password and complete the new student check-in.
```

**Why it is relevant:**
The returned chunk directly explains that students must check in with SEVIS within their first week on campus and complete new student check-in through myPassport.

### Retrieval Test 3

**Query:**
How can WSU students use Pullman Transit without paying a fare each time?

**Top returned chunk:**
Source: WSU Transit Fee Information, chunk index 1, distance 0.3005.

```text
Students rely on transit. Pullman Transit provides as many as 1.4 million rides per year and most of those riders are WSU students!
Students need to simply show their CougarCard to ride the bus!
Pullman Transit provides services Monday through Sunday year-round.
```

**Why it is relevant:**
The returned chunk directly says students need to show their CougarCard to ride the bus.

### Retrieval Test 4

**Query:**
What is the CougarCard used for at WSU?

**Top result:**
WSU CougarCard Center, chunk index 0, distance 0.4236.

**Why it is relevant:**
The returned chunk lists CougarCard uses including university identification, library privileges, meal plan purchases, Cougar CASH, Student Recreation Center access, Pullman Transit, and residence hall/building access.

### Retrieval Test 5

**Query:**
How can students find vegan, vegetarian, halal, or allergen-friendly food at WSU Dining?

**Relevant results:**
The system retrieved WSU International Student Handbook chunks about dining and dietary restrictions, and also retrieved the WSU Dining Services NetNutrition page. The NetNutrition chunk was especially relevant because it describes filtering foods by traits, ingredients, allergens, vegan options, and Halal options.

---

## Grounded Generation

**System prompt grounding instruction:**
The generation step uses a system prompt that explicitly tells the model:

```text
You are a grounded RAG assistant for a WSU Campus Survival Guide.

Rules:
1. Answer using ONLY the provided retrieved context.
2. Do NOT use outside knowledge.
3. If the context does not contain enough information, say exactly:
   "I don't have enough information on that."
4. Be concise and helpful.
5. Do not invent policies, dates, locations, phone numbers, or links.
```

The user prompt also includes the retrieved chunks as context and repeats the instruction to answer only from the retrieved context.

**How source attribution is surfaced in the response:**
Source attribution is appended programmatically from retrieved metadata. The model is not trusted to invent or remember citations. The interface displays a separate “Retrieved from” section containing the source document title, URL, and retrieval distance. The Gradio interface also shows a retrieved chunk preview so the user can see what context supported the answer.

---

## Query Interface

I built a Gradio web interface in `app.py`.

The interface includes:

* A textbox for the user question
* An “Ask” button
* An answer box
* A “Retrieved from” box showing source titles, URLs, and distances
* A retrieved chunk preview box showing the top retrieved chunks

A user can run the app with:

```bash
python app.py
```

Then open:

```text
http://localhost:7860
```

### Sample Interaction Transcript

**User question:**
How can WSU students ride Pullman Transit?

**System answer:**
WSU students can ride Pullman Transit by simply showing their CougarCard.

**Retrieved from:**

* WSU Transit Options
* WSU Pullman Transportation
* WSU Transit Fee Information

The interface also shows the retrieved chunk preview, including the text saying that students show their CougarCard to ride the bus.

---

## Example Responses

### Example Response 1 — Pullman Transit

**Question:**
How can WSU students ride Pullman Transit?

**Answer:**
WSU students can ride Pullman Transit by simply showing their CougarCard.

**Sources shown by the interface:**

* WSU Transit Options
* WSU Pullman Transportation
* WSU Transit Fee Information

### Example Response 2 — CougarCard

**Question:**
What is the CougarCard used for?

**Answer:**
The CougarCard is used for general university identification, library privileges, Resident Meal Plan purchases, Cougar CASH purchases, Student Recreation Center access and rentals, riding Pullman Transit buses, and access to selected residence halls, campus offices, and buildings.

**Sources shown by the interface:**

* WSU CougarCard Center
* WSU Campus Arrival Guide
* WSU International Student Handbook

### Out-of-Scope Response

**Question:**
What are the best hiking trails in Seattle?

**Answer:**
I don't have enough information on that.

This shows that the system can refuse to answer questions that are outside the document collection.

---

## Evaluation Report

The table below records the five evaluation questions from `planning.md`. For each question, I include the expected answer, the system response, retrieval quality, and response accuracy judgment.

| # | Question                                                                                 | Expected answer                                                                                                                                                                                        | System response (summarized)                                                                                                                                                                                                  | Retrieval quality | Response accuracy |
| - | ---------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------- | ----------------- |
| 1 | What should international students use myWSU for before or after arriving at WSU?        | Students use myWSU to manage important university tasks such as admission information, student account details, tuition and fees, class-related information, and other official WSU student services.  | The system said students use myWSU to see their class schedule, pay tuition, and manage important matters. It also said students should know their WSU username and password before arriving.                                 | Relevant          | Accurate          |
| 2 | What should international students do for SEVIS check-in after arriving at WSU?          | International students should complete the required SEVIS check-in process after arriving at WSU as part of their international student arrival requirements.                                          | The system said students must check in with SEVIS within their first week on campus by logging into myPassport with their WSU username and password and completing new student check-in.                                      | Relevant          | Accurate          |
| 3 | How can WSU students use Pullman Transit without paying a fare each time?                | WSU students can ride Pullman Transit by showing or using their CougarCard/WSU student ID because bus access is supported through WSU transit services and student fees.                               | The system said WSU students can ride Pullman Transit by simply showing their CougarCard.                                                                                                                                     | Relevant          | Accurate          |
| 4 | What is the CougarCard used for at WSU?                                                  | The CougarCard is the WSU student ID and can be used for campus services such as dining/Cougar CASH, residence hall access, Student Recreation Center access, Pullman Transit, and other WSU services. | The system listed general university identification, library privileges, meal plan purchases, Cougar CASH, Student Recreation Center access, Pullman Transit, and access to selected residence halls, offices, and buildings. | Relevant          | Accurate          |
| 5 | How can students find vegan, vegetarian, halal, or allergen-friendly food at WSU Dining? | Students can use WSU Dining menu labels and NetNutrition to check ingredients, allergens, and dietary categories such as vegan, vegetarian, halal, gluten-friendly, and other food options.            | The system said students can use NetNutrition to filter foods based on traits, select diet preferences, view nutritional content and ingredients, and get help from registered dietitians.                                    | Relevant          | Accurate          |

**Retrieval quality:** Relevant / Partially relevant / Off-target
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed or exposed a limitation:**
What are the best hiking trails in Seattle?

**What the system returned:**
The system correctly answered:

```text
I don't have enough information on that.
```

However, the retriever still returned weakly related chunks from WSU/Pullman sources, including the WSU International Student Handbook, the Reddit transportation discussion, and the WSU Pullman Transportation page.

**Root cause tied to a specific pipeline stage:**
This is a retrieval-stage limitation. ChromaDB similarity search always returns the top-k nearest chunks, even when none of the chunks are truly relevant. Since the question contains location/travel language, the embedding model retrieved weakly related chunks about Pullman transportation and student life. The generation stage handled this correctly because the grounding prompt instructed the model to refuse unsupported questions.

**What you would change to fix it:**
I would add a stricter relevance threshold or reranking step. For example, if the best distance is above a chosen threshold, the system could return no sources and refuse before calling the LLM. I would also consider a reranker that checks whether the retrieved chunks actually answer the question, not just whether they are semantically nearby.

---

## Spec Reflection

**One way the spec helped you during implementation:**
The planning document helped me make implementation decisions before writing code. For example, I already knew that I wanted to use `all-MiniLM-L6-v2`, ChromaDB, top-k retrieval of 4 chunks, and Groq/Llama for generation. Because the pipeline diagram clearly separated ingestion, chunking, embedding, retrieval, and generation, it was easier to implement and debug one stage at a time.

The evaluation questions in `planning.md` also helped me test whether retrieval was working. Instead of asking random questions, I used specific expected-answer questions to check if the right chunks were being returned.

**One way your implementation diverged from the spec, and why:**
My original plan was to scrape all source URLs directly. In practice, two sources did not scrape cleanly: the WSU International Student Handbook returned a WordPress login page, and Reddit returned very little useful text. I handled this by manually copying useful text into the clean document files and modifying the ingestion script so it would not overwrite manually cleaned files.

Another small divergence is that I kept character-based chunking for Milestone 3 instead of switching immediately to paragraph-aware chunking. I noticed that some chunks had imperfect boundaries, but the total chunk count was reasonable and retrieval worked well enough for the evaluation questions. I documented paragraph-aware chunking as a future improvement.

---

## AI Usage

**Instance 1 — Ingestion and chunking support**

* *What I gave the AI:*
  I gave the AI my `planning.md` sections for the document sources, chunking strategy, and architecture diagram. I asked it to help draft an ingestion and chunking script that could read my WSU source list, clean webpage text, and produce chunks using my planned 900-character chunk size and 200-character overlap.

* *What it produced:*
  It suggested a Python script using `requests`, `BeautifulSoup`, JSONL output, and a `chunk_text()` function. The script gave me a starting structure for reading source URLs, saving raw and cleaned documents, and writing processed chunks to `data/processed/chunks.jsonl`.

* *What I reviewed, changed, or overrode:*
  I checked the script against my actual `sources.md` file and found that the generated parser assumed a Markdown table, while my file used headings like `### 1. Source Title` and `**URL:**`. I changed the parsing logic to match my file format. I also inspected the cleaned text and found that the WSU handbook and Reddit page did not scrape correctly, so I manually cleaned those sources and modified the script so it would reuse existing clean files instead of overwriting them.

**Instance 2 — Retrieval implementation and debugging**

* *What I gave the AI:*
  I gave the AI my retrieval plan from `planning.md`, including `sentence-transformers/all-MiniLM-L6-v2`, ChromaDB, top-k retrieval, and the requirement to preserve source metadata for attribution.

* *What it produced:*
  It helped draft `scripts/embed_and_retrieve.py`, including loading chunks from `chunks.jsonl`, embedding them with SentenceTransformers, storing them in ChromaDB, and printing retrieved chunks with distance scores for my evaluation questions.

* *What I reviewed, changed, or overrode:*
  I ran the retrieval tests myself and inspected the returned chunks and distances. I decided to keep top-k = 4 because the top results were relevant and mostly below 0.5 distance. I also identified a limitation: for the dining/allergen question, the broader handbook chunks ranked above the more specific NetNutrition page. I kept the implementation because it still retrieved the correct information, but I documented this as a limitation and future improvement.

**Instance 3 — Grounded generation and interface**

* *What I gave the AI:*
  I asked the AI to help connect my retriever to Groq/Llama and create a Gradio interface. I specifically required that answers use only retrieved context, that unsupported questions return “I don't have enough information on that,” and that source attribution be visible.

* *What it produced:*
  It helped draft `query.py` for grounded generation and `app.py` for the Gradio interface.

* *What I reviewed, changed, or overrode:*
  I reviewed the grounding prompt to make sure it explicitly prevents outside knowledge. I also made source attribution programmatic by displaying retrieved source titles, URLs, and distance scores from metadata instead of relying only on the LLM to cite sources. Finally, I tested both in-scope questions and an out-of-scope Seattle hiking question to confirm the system refused unsupported answers.

---

## How to Run

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

### 2. Install requirements

```bash
pip install -r requirements.txt
```

### 3. Add Groq API key

Create a `.env` file in the repo root:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

### 4. Run ingestion and chunking

```bash
python scripts/ingest_and_chunk.py
```

This creates cleaned documents and processed chunks.

### 5. Build the vector store

```bash
python scripts/embed_and_retrieve.py --build
```

### 6. Test retrieval

```bash
python scripts/embed_and_retrieve.py --test
```

### 7. Run final evaluation

```bash
python scripts/run_evaluation.py
```

### 8. Run the Gradio app

```bash
python app.py
```

Open the local URL shown in the terminal, usually:

```text
http://localhost:7860
```

---

## Demo Video

The demo video is submitted through the Course Portal. It shows:

1. The Gradio query interface.
2. At least 3 questions answered with source attribution visible.
3. One strong retrieval example about Pullman Transit.
4. One out-of-scope question where the system refuses to answer.
5. A brief walkthrough of the final evaluation report.
