# Technology Stack and Model Strategy

This document describes the target technology stack and model-selection strategy for the Health Psychology AI platform.

The architecture is intentionally model-agnostic.

The system should be able to use different LLM providers and different models for different capabilities without rewriting the core orchestration logic.

---

# 1. Development Environment

## Google Colab

Google Colab is used for:

- development;
- experiments;
- evaluation;
- notebook-based testing;
- reproducible runs.

## GitHub

GitHub is the source of truth for:

- code;
- architecture documentation;
- evaluation artifacts;
- configuration;
- project history.

---

# 2. Core Application Language

## Python

Python is used for:

- orchestration;
- retrieval;
- evaluation;
- tool integration;
- analytics;
- model-provider adapters.

---
# 3. Data Ingestion and Document Processing

The project already supports ingestion of heterogeneous scientific and course sources.

Implemented source formats include:

- PDF;
- HTML;
- Markdown;
- structured CSV data.

## PDF Processing

PDF sources are processed with PyMuPDF.

Implemented functionality includes:

- text-layer extraction;
- ordered page text extraction;
- source-page inspection;
- PDF metadata inspection;
- figure extraction and asset preservation;
- table detection attempts;
- manual structured normalization when automatic table extraction is unreliable.

Example pipeline:

```text
PDF
↓
PyMuPDF
↓
Text / Figures / Table Detection
↓
Visual Validation
↓
Normalized Markdown
```

For the course syllabus, PyMuPDF successfully extracted the text layer, but automatic table detection did not reliably identify the grading tables.

Because the document was small and stable, the tables were manually normalized into structured Markdown after visual verification.

This preserved relationships between:

- grading categories;
- percentages;
- assessment items;
- learning outcomes;
- letter grades;
- grade points.

The project therefore treats document normalization as a quality-sensitive ingestion step rather than assuming that raw PDF extraction is always sufficient.

---

## HTML Processing

Scientific HTML sources are processed using:

- `requests`;
- `BeautifulSoup`;
- HTML structure inspection;
- custom HTML-to-Markdown conversion.

The ingestion process preserves where relevant:

- article headings;
- paragraphs;
- links;
- citations;
- figures;
- figure captions;
- tables;
- source metadata.

External scientific assets can be stored separately and referenced from normalized Markdown.

Example pipeline:

```text
Scientific HTML
↓
requests
↓
BeautifulSoup
↓
Article Structure
↓
Text + Headings + Links + Figures + Tables
↓
Normalized Markdown
```

---

## Normalized Knowledge Format

Different source formats are normalized before retrieval.

```text
PDF
HTML
Markdown
↓
Normalized Markdown
↓
Section-Aware Chunking
↓
Metadata Enrichment
↓
JSONL Knowledge Base
```

The current knowledge base contains 474 chunks.

Chunking configuration:

```text
minimum size: 500 characters
target size: 800 characters
maximum size: 1000 characters
overlap: 120 characters
```

The chunking strategy prefers:

- section boundaries;
- paragraph boundaries;
- sentence boundaries;
- independently understandable chunks.

Each chunk preserves traceability to the original source through metadata.

---

# 4. Retrieval Stack

## Current Scientific Retrieval

The current project already implements a complete local semantic retrieval pipeline.

Technology stack:

```text
sentence-transformers
+
all-MiniLM-L6-v2
+
NumPy
+
FAISS
```

Current implementation:

```text
chunks.jsonl
↓
SentenceTransformer embeddings
↓
384-dimensional vectors
↓
L2 normalization
↓
FAISS IndexFlatIP
↓
Top-K semantic retrieval
```

Inner product over L2-normalized vectors behaves as cosine similarity.

The same embedding model is used for both:

- knowledge-base chunks;
- user queries.

---

## Improved Retrieval

Homework 3 extended the baseline retrieval with:

- metadata filtering;
- candidate retrieval;
- simple hybrid semantic + lexical reranking.

Current hybrid configuration:

```text
semantic score: 70%
keyword score: 30%
```

Evaluation results:

```text
Baseline Top-1 accuracy: 83.3%
Improved Top-1 accuracy: 100%

Baseline Recall@3: 100%
Improved Recall@3: 100%
```

Metadata filtering produced the strongest improvement in the current experiment.

The final project may further evaluate:

- query rewriting;
- reranking;
- alternative embedding models;
- alternative vector stores;
- parent-child retrieval;
- larger domain-specific evaluation sets.

---

# 5. Orchestration

## LangGraph

LangGraph remains the orchestration runtime.

It is responsible for:

- explicit state;
- workflow nodes;
- conditional routing;
- policy gates;
- tool execution paths;
- controlled transitions;
- execution traces.

The architecture uses one controller with several specialized workflows rather than several autonomous agents.

---

# 6. RAG-Assisted Routing

The current HW7 system uses keyword-based routing.

The target architecture replaces this with semantic capability retrieval.

Routing RAG answers:

> Which capability or workflow should handle this request?

The routing knowledge base can contain:

- capability descriptions;
- routing rules;
- positive examples;
- negative examples;
- safety constraints;
- required tools;
- authorization requirements.

Possible capabilities include:

```text
domain_expert
medical_safety
analytics_text2sql
customer_support
clarification
unsupported
```

Routing retrieval should remain separate from scientific knowledge retrieval.

---

# 7. Scientific Knowledge RAG

The Domain-Specific Expert Assistant uses a scientific knowledge retrieval layer.

Current and planned components include:

- document ingestion;
- chunking;
- metadata;
- embeddings;
- vector search;
- FAISS;
- metadata filtering;
- hybrid retrieval;
- retrieved evidence;
- grounded answer generation;
- citations.

Primary sources may include:

- Health Psychology course materials;
- textbooks;
- scientific papers;
- rehabilitation materials;
- psychoeducational sources;
- other curated domain documents.

The LLM should generate answers from retrieved evidence rather than rely only on internal model knowledge.

---

# 8. Analytics / Text2SQL Stack

The Analytics Assistant operates on structured data.

The expected workflow is:

```text
User Question
↓
Analytics Intent
↓
Authorization
↓
Metric / Schema Retrieval
↓
Text2SQL
↓
Query Validation
↓
Read-Only Execution
↓
Result
↓
Natural-Language Explanation
```

Possible technologies include:

- SQL;
- Python;
- Pandas;
- analytics APIs;
- read-only database connections;
- schema retrieval;
- metric definitions.

The LLM should not be treated as the source of truth for numerical calculations.

Trusted computations should be executed by SQL, Python, APIs, or analytical systems.

---

# 9. Customer Support and Clinic Tools

The Customer Support Assistant combines RAG with live operational tools.

Clinic RAG may contain:

- services;
- doctors;
- specializations;
- clinic locations;
- prices;
- FAQ;
- preparation information;
- online consultation rules;
- clinic policies.

Live tools may include:

```text
search_services()
search_doctors()
search_locations()
get_available_slots()
create_booking()
reschedule_booking()
cancel_booking()
```

Static or relatively stable information can come from RAG.

Dynamic information such as current availability should come from live tools or APIs.

Write operations must require explicit user confirmation.

---

# 10. LLM Provider Abstraction Layer

The core system should not depend directly on one LLM provider.

Instead, the application uses an internal abstraction layer.

```text
                    Application
                         │
        ┌────────────────┼────────────────┐
        ↓                ↓                ↓
      Router          Workflows        Evaluator
        │                │                │
        └────────────────┼────────────────┘
                         ↓
                  LLM Provider Layer
                         ↓
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          OpenAI      Anthropic     Azure
```

The application should interact with a common internal interface such as:

```text
generate()
generate_structured()
use_tools()
```

Vendor-specific API logic should remain inside provider adapters.

A future code structure may look like:

```text
providers/
├── base.py
├── openai_provider.py
├── anthropic_provider.py
├── azure_openai_provider.py
└── config.py
```

This allows provider changes without rewriting LangGraph workflows.

---

# 11. Model Roles

The project does not assume that one model is optimal for every task.

Different workflows have different requirements.

---

## 11.1 Router Model

Primary requirements:

- low latency;
- low cost;
- reliable structured output;
- reliable intent recognition;
- predictable routing.

A large reasoning model should normally not be required for routing.

---

## 11.2 Domain Expert Model

Primary requirements:

- strong reasoning;
- high-quality synthesis;
- grounded generation;
- instruction following;
- citation quality;
- handling of uncertainty.

A stronger reasoning model may be justified for complex domain questions.

Examples:

```text
Compare several scientific explanations.

Synthesize evidence from multiple sources.

Explain uncertainty or conflicting evidence.

Reason across health, behaviour, and work-function context.
```

---

## 11.3 Analytics / Text2SQL Model

Primary requirements:

- structured output;
- SQL reasoning;
- schema understanding;
- metric interpretation;
- reliable tool calling;
- constraint following.

The model proposes or structures queries.

Deterministic systems validate and execute them.

---

## 11.4 Customer Support Model

Primary requirements:

- low latency;
- low cost;
- good conversational quality;
- reliable tool calling;
- good instruction following.

Most customer-support requests should not require an expensive reasoning model.

Examples:

```text
Find a doctor.

Check a clinic location.

Explain a service.

Find available slots.

Prepare a booking action.
```

---

## 11.5 Evaluator Model

Semantic evaluation may use a separate model from the production workflow.

This makes it possible to compare:

```text
production model
vs
independent evaluator
```

The evaluator can also use a different provider.

LLM-as-a-judge should only be used when deterministic evaluation is insufficient.

---

# 12. Model Escalation Strategy

The strongest model should not automatically handle every request.

A possible strategy is:

```text
Simple Request
↓
Fast / Lower-Cost Model
```

```text
Complex Domain Synthesis
↓
Strong Reasoning Model
```

```text
High Uncertainty
↓
Strong Reasoning Model
+
Safety Workflow
```

```text
High-Risk Situation
↓
Safety Workflow
+
Human Escalation When Required
```

Examples:

```text
"What is the COM-B model?"
→ standard domain model
```

```text
"Compare how fear, avoidance, stress, and pain may interact across several studies."
→ stronger reasoning model
```

Model escalation should be measurable.

---

# 13. Provider and Model Configuration

Provider and model selection should be configuration-driven.

Conceptually:

```text
router:
    provider: configurable
    model_profile: fast

domain_expert:
    provider: configurable
    model_profile: reasoning

analytics:
    provider: configurable
    model_profile: structured

customer_support:
    provider: configurable
    model_profile: fast

evaluator:
    provider: configurable
    model_profile: evaluation
```

This makes cross-provider experiments possible.

For example:

```text
Same Test Set
+
Same Retrieval
+
Same Workflow
+
Same Prompt
↓
OpenAI
vs
Anthropic
vs
Azure-hosted model
```

---

# 14. Model Selection Criteria

Models should be compared across several dimensions.

```text
Quality
+
Groundedness
+
Task Success
+
Latency
+
Cost
+
Reliability
```

The most expensive model is not automatically the best production choice.

The cheapest model is also not automatically the best choice.

The goal is to find the best trade-off for each capability.

---

# 15. Deterministic Components

Not every task should be delegated to an LLM.

The following should remain deterministic where possible:

## Authorization

```text
trusted backend role
→ allow / deny
```

## Medical Safety

```text
explicit safety policy
→ allowed / restricted behavior
```

## Analytics

```text
query validation
read-only database access
deterministic computation
```

## Booking

```text
explicit confirmation
→ write action
```

## Evaluation

```text
exact route
exact tool usage
expected policy decision
runtime errors
latency
```

Semantic models are used where semantic reasoning adds value.

---

# 16. Observability Stack

Every production-style run should eventually record:

```text
workflow
route
provider
model
input_tokens
output_tokens
model_calls
retrieved_sources
retrieval_scores
tools_called
authorization_decision
safety_decision
latency_ms
estimated_cost
errors
task_success
```

These traces support:

- debugging;
- evaluation;
- model comparison;
- cost analysis;
- architecture improvement.

---

# 17. Evaluation Stack

The project uses a trace-first evaluation strategy.

Evaluation may include:

- deterministic test cases;
- routing accuracy;
- retrieval metrics;
- Recall@K;
- groundedness;
- citation correctness;
- task success;
- safety compliance;
- SQL correctness;
- tool execution correctness;
- booking success;
- latency;
- token usage;
- estimated cost.

---

# 18. Current vs Target Stack

## Current Project

Already implemented or demonstrated during previous homework stages:

```text
Python
GitHub
Google Colab
Health Psychology knowledge base
chunking
embeddings
FAISS
metadata filtering
hybrid retrieval
authorization logic
controlled workflows
LangGraph orchestration
execution traces
```

## Target Final Architecture

Planned evolution:

```text
RAG-assisted semantic controller
+
specialized Domain Expert workflow
+
Analytics / Text2SQL workflow
+
Customer Support / Clinic Booking workflow
+
model-agnostic provider layer
+
multi-provider model experiments
+
trace-based evaluation
+
cost tracking
```

---

# 19. Technology Selection Principle

Technology should be selected based on the use case rather than vendor preference.

The architecture follows these principles:

1. keep orchestration independent from the LLM provider;
2. use RAG where external knowledge is required;
3. use tools for live or transactional data;
4. use deterministic logic for authorization, validation, and sensitive actions;
5. use stronger models only where additional reasoning quality is justified;
6. evaluate quality, latency, and cost together;
7. keep the system replaceable and testable across vendors.
