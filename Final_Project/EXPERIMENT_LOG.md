# Experiment Log

Short record of experiments, results and architecture decisions for the Final Project.

---

## Results Summary

| Experiment | Result | Key finding |
|---|---:|---|
| Baseline — English keywords | 7.7% accuracy | Does not work for Ukrainian traffic |
| A — Ukrainian rules | 84.6% accuracy | Best overall accuracy and latency |
| B — Translate then route | INVALID | API/model errors; rerun required |
| C — Multilingual embeddings | 69.2% accuracy | Better safety recall, higher latency |
| Taxonomy v2 + RAG + Claude | Working end-to-end | Capability + policy separation works |
| Taxonomy v2 evaluation | Completed | 100% preferred/allowed capability accuracy, 100% safety recall, 0% unsafe routes |
| Retrieval runtime caching | Warm retrieval 5456.57 ms → 459.48 ms | Observability exposed repeated model/index loading; caching reduced warm retrieval latency ~11.9× |

---

## Experiment 001 — English Keyword Baseline

**Status:** Completed

```text
Routing accuracy:       7.7%
Real-user accuracy:     0.0%
Medical-safety recall:  0.0%
```

**Finding:** HW7 English keyword routing is not suitable for Ukrainian requests.

**Decision:** Keep as the `before` baseline.

---

## Experiment 002 — Ukrainian Rules

**Status:** Completed

```text
Routing accuracy:       84.6%
Real-user accuracy:     71.4%
Medical-safety recall:  66.7%
Latency:                ~0.07 ms
Paid API cost:          $0
```

**Finding:** Best overall accuracy and latency, but medical-safety recall is still insufficient.

**Decision:** Strong baseline, not yet production-ready.

---

## Experiment 003 — Translate Then Route

**Status:** Invalid — rerun required

Translation API/model failures made the run invalid.

The evaluator also allowed a failed call to count as correct when fallback happened to match `clarification`.

**Decision:** Do not compare Strategy B until execution errors are fixed.

---

## Experiment 004 — Multilingual Semantic Router

**Status:** Completed

```text
Routing accuracy:       69.2%
Real-user accuracy:     71.4%
Medical-safety recall:  83.3%
Latency:                ~32 ms
```

**Finding:** Semantic routing improves safety recall but is slower and less accurate overall than Ukrainian rules.

**Decision:** Semantic does not automatically mean better.

---

## Experiment 005 — Conversation & Funnel Observability

**Status:** Implemented

Tracked:

```text
turns
domain engagement
risk
LLM calls
tokens
AI cost
IVR CTA
website click
booking
```

Demo policy:

```text
high risk
→ professional-care pathway immediately

low/moderate risk
→ useful conversation
→ soft IVR CTA later
```

Future KPI:

```text
AI cost per booked consultation
```

No production conversion results are claimed.

---

## Experiment 006 — Taxonomy v2 + RAG + Claude

**Status:** Working end-to-end demo

### Change

Replaced flat routing:

```text
query → expected_route
```

with multidimensional routing:

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

Core principle:

```text
preferred_capability
= what should lead the response

required_policy
= what constraints must be applied
```

Medical safety is a policy overlay, not a competing topic.

### Demo results

| Query | Capability | Policy | Result |
|---|---|---|---|
| `Що таке Health Psychology?` | health_psychology | none | RAG + Claude grounded answer |
| Medication + exercise request | medical_safety_workflow | medical_safety | Unsafe individualized advice blocked |
| High-risk symptoms | health_psychology | medical_safety | RAG context + deterministic safety + IVR navigation |
| `Ергономічний стул` | health_psychology | none | Clarification allowed |

Positive RAG control:

```text
Query: Що таке Health Psychology?
Top retrieval score: 0.5333
Source: Ogden 2019 Health Psychology
Section: The Background of Health Psychology
```

High-risk case:

```text
Health Psychology RAG
→ insufficient evidence for specific symptoms

medical_safety policy
→ no diagnosis / treatment advice

care navigation
→ IVR professional consultation
→ online or offline
```

**Finding:** Routing quality, safety policy and Knowledge Base coverage are separate concerns and should be evaluated separately.

---

## Experiment 007 — Taxonomy v2 Evaluation Contract

**Status:** Completed

The previous evaluator used:

```text
correct = actual_route == expected_route
```

This was too rigid for multidimensional Health Psychology requests.

The new evaluator separates:

```text
preferred capability
allowed capability
risk class
required policy
medical-safety activation
clarification appropriateness
```

### Evaluation set

```text
13 cases total
6 controlled
7 real-user-derived
```

The old dataset is preserved as the `before` baseline:

```text
data/routing_eval_ua.jsonl
```

The new multidimensional ground truth is stored separately:

```text
data/routing_eval_v2.jsonl
```

### Results

```text
Preferred-capability accuracy:         100.0%
Allowed-capability accuracy:           100.0%
Risk-class accuracy:                    92.3%
Required-policy accuracy:              100.0%
Medical-safety recall:                 100.0%
Unsafe-route rate:                       0.0%
Clarification appropriateness:         100.0%
Real-user allowed-capability accuracy: 100.0%
Failed cases:                            0
```
These results are regression-test performance on the current 13-case evaluation set. The deterministic rules were iteratively refined against this small set, so the results should not be interpreted as held-out generalization or production performance.

### Finding

The multidimensional evaluator shows a stronger picture than flat route accuracy alone.

The system correctly selected an allowed capability for every evaluated request, including all real-user-derived cases.

All requests that required the `medical_safety` policy activated it.

No evaluated request was routed outside its allowed capability set.

Risk-class accuracy remained at 92.3%, showing that risk labelling and safety-policy activation are related but separate evaluation dimensions.

### Decision

Use Taxonomy v2 as the final `after` evaluation contract.

Keep the original flat-routing evaluation only as the historical `before` baseline.

---

## Current Status

```text
Baseline routing          measured
Strategy A                measured
Strategy B                invalid
Strategy C                measured
Taxonomy v2               implemented
Taxonomy v2 evaluation    completed
Health Psychology RAG     connected
Claude synthesis          connected
Medical-safety overlay    implemented
IVR care navigation       implemented
Online/offline option     implemented
Funnel observability      implemented
```

## Experiment 008 — Retrieval Runtime Caching

**Status:** Completed

### Motivation

Runtime observability showed that local retrieval was unexpectedly slower than the Claude synthesis step.

Before optimization:

```text
Average FAISS retrieval latency: 4722.84 ms
Average Claude latency:          4032.69 ms
```

Inspection showed that the retrieval path reloaded the following components for every RAG turn:

```text
SentenceTransformer model
FAISS index
retrieval chunks
```

### Change

The retrieval runtime was changed from per-request initialization to process-level reuse:

```text
first RAG turn
→ load chunks
→ load FAISS index
→ load embedding model
→ retrieve

subsequent RAG turns
→ reuse chunks
→ reuse FAISS index
→ reuse embedding model
→ retrieve
```

The runtime objects are cached with:

```text
@lru_cache(maxsize=1)
```

The experiment was tracked separately as:

```text
experiment_id = taxonomy_v2_rag_demo_cached_v2
```

### Same 3-turn benchmark

The same three requests were used before and after the change:

```text
1. General Health Psychology information
2. Medication + exercise safety request
3. High-risk symptom request
```

Runtime behavior remained:

```text
3 conversation turns
3 taxonomy classifications
2 retrieval calls
2 Claude calls
```

The medication-safety request continued to use the deterministic safety workflow:

```text
LLM calls: 0
tokens:    0
LLM cost:  $0
```

### Results

Before caching:

```text
Average retrieval latency: 4722.84 ms
```

After caching:

```text
Average retrieval latency: 2958.02 ms

Cold retrieval:
5456.57 ms

Warm cached retrieval:
459.48 ms
```

Warm-cache speedup:

```text
~11.9×
```

The post-cache Claude runtime was:

```text
Provider:                   Anthropic
Model:                      claude-haiku-4-5-20251001
LLM calls:                  2
Input tokens:               1623
Output tokens:              607
Total tokens:               2230
Estimated AI cost:          $0.004658
Average cost per LLM call:  $0.002329
Average Claude latency:     4383.73 ms
```

### Finding

Observability exposed a system bottleneck that was not caused by the LLM.

The main avoidable latency came from repeatedly initializing the local retrieval runtime.

Caching the embedding model, FAISS index and retrieval chunks reduced warm retrieval latency from approximately 5.5 seconds to 0.46 seconds.

The average post-cache retrieval latency still includes the first cold-start request, so warm-cache latency is the better indicator of steady-state performance.

### Decision

Keep process-level retrieval caching in the final architecture.

Treat cold-start initialization separately from steady-state retrieval latency in future performance evaluation.

Do not interpret this small local benchmark as a production latency benchmark.