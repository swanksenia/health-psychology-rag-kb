# Final Project — Multidimensional Ukrainian Routing with Safety Policy Overlay

## Product

**IVR Health Psychology & Chronic Back Pain Domain-Specific Expert Assistant**

The final project extends the existing RAG, safety, LangGraph and observability layers.

The focused technical improvement is:

> **replace flat single-label routing with multidimensional Ukrainian routing that separates response capability from safety policy.**

Core principle:

```text
preferred_capability
= what should lead the response

required_policy
= what constraints must be applied
```

This allows a request to remain in a Health Psychology context while simultaneously activating medical-safety restrictions.

---

## Architecture

```text
User request
↓
Deterministic multidimensional taxonomy
↓
intent + context + risk
↓
preferred capability + required policy
↓
Deterministic policy gate
↓
Health Psychology RAG
OR
medical-safety workflow
OR
clarification
OR
analytics
↓
Grounded response
+
deterministic care navigation when required
↓
Trace + conversation + funnel observability
```

Medical safety is a policy overlay, not a competing topic.

---

## Before

The original HW7-style router relied on English keyword matching and one expected route.

Measured baseline:

```text
Routing accuracy:       7.7%
Real-user accuracy:     0.0%
Medical-safety recall:  0.0%
```

Two additional routing approaches were evaluated:

```text
Native Ukrainian rules:
accuracy:               84.6%
medical-safety recall:  66.7%

Multilingual embeddings:
accuracy:               69.2%
medical-safety recall:  83.3%
```

The translate-then-route experiment was invalid because of API/model execution errors and is not used for the final comparison.

---

## Final Taxonomy v2

The router now produces:

```text
primary_intent
secondary_intent
risk_class
requested_action
domain
preferred_capability
required_policy
allowed_capabilities
forbidden_capabilities
needs_clarification
```

Evaluation set:

```text
13 cases total
6 controlled
7 anonymized real-user-derived
```

Results:

```text
Preferred-capability accuracy:         100.0%
Allowed-capability accuracy:           100.0%
Risk-class accuracy:                    92.3%
Required-policy accuracy:              100.0%
Medical-safety recall:                 100.0%
Unsafe-route rate:                       0.0%
Clarification appropriateness:         100.0%
Real-user allowed-capability accuracy: 100.0%
```

These are regression-test results on the current small evaluation set, not held-out production performance.

---

## RAG and safety

For Health Psychology requests:

```text
FAISS retrieval
↓
Ogden 2019 Health Psychology evidence
↓
Claude grounded synthesis
```

Claude is instructed to use retrieved evidence only and report insufficient evidence when the Knowledge Base does not support the request.

Medical-safety logic remains deterministic.

The assistant does not provide:

- diagnosis;
- medication dosing or recommendations;
- individualized exercise prescriptions;
- individualized treatment prescriptions.

High-risk or individualized medical requests can be directed to IVR professional-care navigation for chronic pain or neurological symptoms.

---

## Observability

The project tracks:

```text
conversation
turns
risk state
taxonomy classification
retrieval
LLM calls
provider
model
prompt version
tokens
latency
estimated AI cost
success / error
IVR funnel events
```

A clean 3-turn benchmark produced:

```text
Conversation turns:          3
LLM calls:                   2
Total tokens:                2230
Estimated AI cost:           $0.004658
Average cost / turn:         $0.00155267
```

The medication-safety turn required:

```text
LLM calls: 0
tokens:    0
LLM cost:  $0
```

Runtime tracing also exposed repeated retrieval initialization as a bottleneck.

After caching the embedding model, FAISS index and chunks:

```text
cold retrieval latency:         5456.57 ms
warm cached retrieval latency:   459.48 ms
warm-cache speedup:              ~11.9×
```

This is a local benchmark and should not be interpreted as production latency.

---

## Location handling

Location is requested only when locality is required.

```text
location needed
→ ask permission
→ obtain approximate location
→ confirm city with user
→ store confirmed city only
```

Precise coordinates are not persisted by the demo.

Browser demo:

```text
web/location_consent_demo.html
```

---

## Run

Install dependencies:

```bash
pip install -r requirements.txt
```

For Claude grounded synthesis:

```bash
export ANTHROPIC_API_KEY="..."
```

Run Taxonomy v2 evaluation:

```bash
python scripts/evaluate_taxonomy_v2.py
```

Run interactive end-to-end demo:

```bash
python -u scripts/taxonomy_demo.py
```

Summarize runtime traces:

```bash
python scripts/summarize_traces.py
```

Run deterministic tests:

```bash
pytest -q
```

Historical routing experiments:

```bash
python scripts/evaluate_offline.py
python scripts/multilingual_router.py
```

---

## Main artifacts

```text
data/routing_eval_ua.jsonl
data/routing_eval_v2.jsonl

scripts/evaluate_taxonomy_v2.py
scripts/taxonomy_demo.py
scripts/summarize_traces.py

outputs/taxonomy_v2_results.json
outputs/taxonomy_v2_summary.json
outputs/conversation_traces.jsonl
outputs/observability_summary.json

FINAL_IMPROVEMENT.md
ARCHITECTURE_CARD.md
EXPERIMENT_LOG.md
ROUTING_TAXONOMY.md
```

---

## Main limitation

The current Knowledge Base is based on Health Psychology material and does not provide comprehensive back-pain, neurological or pharmacological coverage.

Therefore:

```text
correct routing
≠
correct safety policy
≠
sufficient knowledge coverage
```

These layers are evaluated separately.

---

## Final result

The final improvement changes the decision model from:

```text
query
→ one route
```

to:

```text
query
→ intent + context + risk
→ preferred capability + required policy
→ grounded execution with deterministic safety controls
```

The main engineering conclusion is that **routing quality, medical safety and Knowledge Base coverage should be modeled and evaluated as separate layers**.