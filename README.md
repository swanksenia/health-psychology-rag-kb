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
