# Health Psychology AI — Quality Report

## 1. Evaluation Scope

The system was evaluated as a product rather than as a sequence of homework assignments.

The evaluation framework covers product quality, routing, safety, authorization, retrieval, groundedness, runtime behavior, latency, token usage, economics, and cost control.

Earlier course implementations are treated as implementation evidence for current product capabilities.

---

## 2. Current Product Evaluation

Current executable cases: **12**

- PASS: **2**
- PARTIAL: **6**
- FAIL: **4**

Full success rate: **16.7%**

Non-fail rate: **66.7%**

---

## 3. Main Product Findings

### Routing

Routing accuracy: **41.7%**

The current keyword-based controller works for several explicit English requests but performs poorly on Ukrainian, colloquial, safety-sensitive, and mixed-intent requests.

This supports moving beyond narrow keyword routing.

### Answer Quality

Correct routing does not guarantee product success.

Manual review showed that the current Health Psychology answer layer often returns generic context instead of answering the specific user question.

### Safety

Safety behavior is incomplete.

A high-risk symptom request received generic clarification instead of safety-oriented handling.

### Authorization

Both positive and negative analytics authorization controls passed.

Deterministic authorization is currently more reliable than semantic routing.

---

## 4. Failure Taxonomy

- ANSWER_QUALITY_FAILURE: **8**
- SAFETY_FAILURE: **1**
- ROUTING_FAILURE: **1**

The dominant observed failure category is `ANSWER_QUALITY_FAILURE`.

This means product improvement should not focus on routing alone.

---

## 5. Performance

Measured local deterministic orchestration latency:

- average: **2.722 ms**
- median: **2.068 ms**
- P95: **5.708 ms**

These values exclude real model inference, embeddings, network latency, production retrieval, and production backend calls.

They must not be interpreted as production latency.

---

## 6. Token and Cost Observability

Real provider token usage and real model cost are not available in the current orchestration baseline.

No synthetic token or cost values were introduced.

The target observability layer will capture:

- input tokens;
- output tokens;
- cached tokens;
- reasoning tokens;
- embedding tokens;
- judge tokens;
- model calls;
- tool calls;
- retries;
- escalation;
- model cost;
- embedding cost;
- judge cost;
- backend cost;
- total cost per run.

The primary economics KPI is:

`cost per successful task`

---

## 7. Multilingual Routing Experiment

The current evaluation identified Ukrainian routing as a measurable failure mode.

Three strategies were defined:

### ML_A — Native Ukrainian

`Ukrainian query -> direct routing`

### ML_B — Translate Then Route

`Ukrainian query -> English translation -> routing`

### ML_C — Multilingual Semantic / RAG Routing

`Ukrainian query -> multilingual semantic retrieval -> capability selection`

The strategies should be compared on:

- routing accuracy;
- task success;
- token usage;
- model calls;
- latency;
- total cost;
- cost per correct routing decision;
- cost per successful task.

Translation should not be preferred simply because English may consume fewer tokens.

The additional translation step may increase total workflow cost and latency.

---

## 8. Model Execution Strategies

### S1 — Strong Model Everywhere

Simple execution policy but potentially unnecessary cost.

### S2 — Cheap First + Escalation

Potentially cheaper for simple tasks, but retries and escalation may erase savings.

### S3 — Workflow-Specific Models

Different models can be selected for routing, generation, and safety-sensitive workflows.

The preferred strategy should optimize:

`quality × latency × total workflow cost`

---

## 9. Runtime Cost Guardrails

Current engineering defaults:

- maximum model calls: **4**
- maximum tool calls: **6**
- maximum retries: **2**

Token and USD thresholds remain unconfigured until real provider usage is measured.

Future guardrails should also include:

- maximum total tokens;
- maximum estimated cost per task.

---

## 10. Architecture Decisions

### Decision 1 — Keep deterministic authorization

Authorization should remain outside free-form model reasoning.

### Decision 2 — Replace narrow keyword routing

Target direction: `semantic / RAG-assisted capability routing`.

### Decision 3 — Separate routing RAG from knowledge RAG

1. capability retrieval for routing;
2. scientific knowledge retrieval for grounded answers.

### Decision 4 — Improve answer generation independently

Routing success and answer quality must be evaluated separately.

### Decision 5 — Add explicit medical-safety handling

Safety-sensitive requests require a dedicated policy path.

### Decision 6 — Make model selection cost-aware

Model selection should optimize `quality × latency × cost`.

### Decision 7 — Protect runtime budgets

Agentic workflows should have explicit limits on model calls, tool calls, retries, tokens, and cost.

---

## 11. Target Architecture

User Request

→ Safety / Authorization Gates

→ RAG-Assisted Capability Controller

→ Health Psychology Expert / Analytics Assistant / future Support & Booking

→ Knowledge RAG or Tool / Backend Workflow

→ Observability Layer

→ quality / latency / tokens / cost / retries

→ Runtime Cost Guardrails

---

## 12. Final Conclusion

The evaluation shows that the current product does not have one single quality problem.

Different system layers fail independently.

Measured evidence shows:

- authorization is currently reliable;
- explicit English routing works for some requests;
- multilingual and mixed-intent routing are weak;
- answer generation is the dominant quality problem;
- safety handling requires a dedicated path;
- real token and cost observability are still missing.

The target system should combine:

- deterministic policy gates;
- semantic / RAG-assisted capability routing;
- grounded domain RAG;
- selective stronger-model escalation;
- token and cost observability;
- runtime cost guardrails.

The product economics goal is:

`cost per successful task`

while preserving quality and safety.