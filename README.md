# Health Psychology RAG Knowledge Base

## Subject Area

This project prepares a knowledge base for a future chatbot focused on **health psychology**.

The knowledge base covers:

- relationships between psychological and physical health;
- stress and illness;
- health behaviour change;
- behavioural intervention design;
- course concepts and learning requirements.

## Pipeline

    raw sources
    → normalized Markdown documents
    → section-aware chunking
    → metadata enrichment
    → JSONL knowledge base
    → embeddings and FAISS index

## Sources

The project contains four source documents:

1. `ogden_2019_health_psychology.pdf`
2. `wright_2019_3p_disease_model.html`
3. `michie_2011_behaviour_change_wheel.html`
4. `course_syllabus.pdf`

Original files are stored in `data/raw/`.

Normalized Markdown documents are stored in `data/normalized/`.

## Chunking Strategy

The documents were split using a section-aware chunking strategy.

- minimum chunk size: 500 characters;
- target chunk size: 800 characters;
- maximum chunk size: 1000 characters;
- overlap: 120 characters;
- section headings are preserved;
- paragraph and sentence boundaries are preferred;
- short self-contained sections are retained.

The final knowledge base contains **474 chunks**.

## Metadata Structure

Each JSONL record contains:

| Field | Description |
|---|---|
| `chunk_id` | Unique chunk identifier |
| `document_id` | Source document identifier |
| `source_file` | Original source filename |
| `chunk_index` | Sequential position within the document |
| `section` | Source section heading |
| `text` | Chunk content |

The processed knowledge base is stored in `data/processed/chunks.jsonl`.

## Chunk Examples

### Example 1

    {
      "chunk_id": "health_psychology_course_syllabus__0000",
      "document_id": "health_psychology_course_syllabus",
      "source_file": "data/raw/course_syllabus.pdf",
      "chunk_index": 0,
      "section": "Document overview",
      "text": "Syllabus for Introduction to Health Psychology Credits: 3 PSYC 1111 Instructor Contact Information: You can always send your instructor a private message through the Brightspace Messaging system, accessible via the envelope (Messages) icon in the top navigation bar. Once logged into your course, click your instructor’s profile page to see all the ways you can communicate with them, including their email address. Course Description Health psychology focuses on the dynamic interaction between biological, social, and psychological factors that influence physical health and illness, aiming to promote overall well-being and prevent diseases. This course is designed to provide students with an introduction to the field of health psychology."
    }

**Why this chunk works:** It preserves the source document, section, sequence, and enough context to be understood independently.

### Example 2

    {
      "chunk_id": "wright_2019_3p_disease_model__0000",
      "document_id": "wright_2019_3p_disease_model",
      "source_file": "data/raw/wright_2019_3p_disease_model.html",
      "chunk_index": 0,
      "section": "Daniel W McNeil",
      "text": "- Author information - Article notes - Copyright and License information Edited by: Silvia Serino, Lausanne University Hospital (CHUV), Switzerland Reviewed by: Anna Sedda, Heriot-Watt University, United Kingdom; Paola Cardinali, University of Genoa, Italy *Correspondence: Casey D. Wright, cdw0022@mix.wvu.edu Daniel W. McNeil, dmcneil@wvu.edu This article was submitted to Psychology for Clinical Settings, a section of the journal Frontiers in Psychology Received 2019 Mar 12; Accepted 2019 Oct 22; Collection date 2019. This is an open-access article distributed under the terms of the Creative Commons Attribution License (CC BY). The use, distribution or reproduction in other forums is permitted, provided the original author(s) and the copyright owner(s) are credited and that the original publication in this journal is cited, in accordance with accepted academic practice. No use, distribution or reproduction is permitted which does not comply with these terms."
    }

**Why this chunk works:** It preserves the source document, section, sequence, and enough context to be understood independently.

### Example 3

    {
      "chunk_id": "michie_2011_behaviour_change_wheel__0002",
      "document_id": "michie_2011_behaviour_change_wheel",
      "source_file": "data/raw/michie_2011_behaviour_change_wheel.html",
      "chunk_index": 2,
      "section": "Results",
      "text": "Nineteen frameworks were identified covering nine intervention functions and seven policy categories that could enable those interventions. None of the frameworks reviewed covered the full range of intervention functions or policies, and only a minority met the criteria of coherence or linkage to a model of behaviour. At the centre of a proposed new framework is a 'behaviour system' involving three essential conditions: capability, opportunity, and motivation (what we term the 'COM-B system'). This forms the hub of a 'behaviour change wheel' (BCW) around which are positioned the nine intervention functions aimed at addressing deficits in one or more of these conditions; around this are placed seven categories of policy that could enable those interventions to occur. The BCW was used reliably to characterise interventions within the English Department of Health's 2010 tobacco control strategy and the National Institute of Health and Clinical Excellence's guidance on reducing obesity."
    }

**Why this chunk works:** It preserves the source document, section, sequence, and enough context to be understood independently.

### Example 4

    {
      "chunk_id": "ogden_2019_health_psychology__0000",
      "document_id": "ogden_2019_health_psychology",
      "source_file": "data/raw/ogden_2019_health_psychology.pdf",
      "chunk_index": 0,
      "section": "Overview",
      "text": "For centuries health professionals have recognized that there are psychological consequences of being ill. A diagnosis of cancer or diabetes can make people anxious or depressed. This course will draw upon health psychology, public health, and community psychology to emphasize how psychology can also contribute to the cause, progression, experience, and outcomes of any physical illness. This course will highlight the many roles that psychology plays in physical illness from i) being and staying well and the role of health behaviors and behavior change; ii) becoming ill with a focus on illness beliefs, symptom perception, help-seeking and communication with health professionals; iii) being ill in terms of stress, pain, and chronic illnesses such as obesity, coronary heart disease, and cancer; iv) the role of gender in health, and v) health outcomes in terms of Quality of Life and longevity."
    }

**Why this chunk works:** It preserves the source document, section, sequence, and enough context to be understood independently.

## Quality Review

### What worked well

- Four source documents were normalized into a consistent Markdown format.
- Chunking preserves document sections and semantic boundaries.
- Every chunk has stable identifiers and source metadata.
- No chunk exceeds the configured maximum size.
- The JSONL file was validated for structure and unique chunk IDs.
- Section metadata supports traceability and future citations.

### What could be improved

- Some naturally short sections remain below the preferred minimum size because they are meaningful standalone units.
- Additional metadata such as `title`, `language`, `domain`, and `document_type` could be added later.
- Retrieval quality should be evaluated with a dedicated test-question set.
- Future work could compare section-aware chunking with semantic or parent-child chunking.

## Optional Retrieval Extension

Beyond the core homework requirements, the project also includes:

- embeddings in `data/processed/embeddings.npy`;
- a FAISS vector index in `data/processed/faiss.index`;
- a successful semantic-search test over all 474 chunks.

---

## Homework 2 — Basic Semantic Retrieval Layer

### Goal

Build a baseline semantic retrieval layer for the PSYC 1111 Health Psychology knowledge base using the chunks prepared in Homework 1.

### Retrieval pipeline

```text
chunks.jsonl
→ embedding generation
→ L2 normalization
→ FAISS vector index
→ query embedding
→ top-k semantic search
→ retrieved chunks with scores and metadata
```

### Implementation

- **Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Embedding dimension:** `384`
- **Vector index:** FAISS `IndexFlatIP`
- **Similarity approach:** inner product over L2-normalized vectors, which behaves like cosine similarity
- **Number of indexed chunks:** `474`
- **Default top-k:** `3`

The same embedding model is used for both knowledge-base chunks and user queries.

FAISS stores the vectors, while chunk text and metadata remain in JSONL format. The position of each vector in the index corresponds to the position of the related chunk in `chunks_for_retrieval.jsonl`.

### Input

```text
data/processed/chunks.jsonl
```

Each chunk includes:

- `chunk_id`
- `document_id`
- `source_file`
- `chunk_index`
- `section`
- `text`

### Generated artifacts

```text
data/processed/chunks_for_retrieval.jsonl
index/embeddings.npy
index/faiss.index
outputs/retrieval_examples.md
data/notebooks/HW2_Semantic_Retrieval.ipynb
```

### Running the notebook

Open the following notebook in Google Colab:

```text
data/notebooks/HW2_Semantic_Retrieval.ipynb
```

The notebook is organized into stages:

1. environment setup;
2. connection to the private GitHub repository;
3. loading Homework 1 chunks;
4. embeddings and similarity demonstration;
5. FAISS index creation;
6. semantic search;
7. retrieval evaluation;
8. conclusion.

Run the cells in order from top to bottom.

The notebook requires:

```text
sentence-transformers==3.0.1
faiss-cpu==1.8.0.post1
numpy==1.26.4
```

### Retrieval evaluation

The retrieval layer was evaluated using six representative queries covering:

- the biopsychosocial model;
- the COM-B model;
- the Behaviour Change Wheel;
- the 3P model of disease;
- stress and physical health;
- Health Psychology course topics.

For every query, the system returns:

- rank;
- similarity score;
- `chunk_id`;
- document and source metadata;
- section;
- text preview.

Detailed top-3 results and relevance comments are available in:

```text
outputs/retrieval_examples.md
```

### Results

The baseline semantic retrieval layer performs well for focused conceptual questions about clearly named Health Psychology models and topics.

Retrieval was especially effective for questions about:

- the biopsychosocial model;
- the Behaviour Change Wheel;
- the 3P model;
- stress and physical health.

Retrieval was weaker for broad navigational questions and questions requiring an exact list from a specific document.

### Current limitations

The current implementation uses semantic vector similarity only. It does not yet include:

- metadata filtering;
- hybrid lexical and semantic search;
- reranking;
- query rewriting;
- LLM-generated answers.
