# Experiment Log

## Purpose

This document is the working experiment and decision log for the Final Project:

**IVR Health Psychology & Chronic Back Pain Domain-Specific Expert Assistant — Cost-Aware Ukrainian Routing**

It records:

- hypotheses;
- implementation changes;
- evaluation runs;
- measured results;
- failures and bugs;
- architecture decisions;
- remaining questions;
- next experiments.

The goal is to keep measured evidence separate from assumptions and to avoid rewriting project history after the fact.

---

# Experiment 001 — Ukrainian Routing Baseline

**Date:** 2026-09-02  
**Status:** Completed

## Question

How well does the existing HW7-style English keyword router work for Ukrainian user requests?

## Hypothesis

The existing router is expected to perform poorly because it relies on predefined English keywords while the target IVR user may write naturally in Ukrainian.

## Dataset

Current evaluation set:

```text
13 total cases
6 controlled cases
7 anonymized real-user-derived cases
6 expected medical-safety cases
```

Main routes:

```text
health_psychology
back_pain_medical_request
analytics
clarification
```

## Baseline

```text
BASELINE_HW7_english_keywords
```

## Measured result

```text
Routing accuracy:        1 / 13 = 7.7%
Real-user accuracy:      0 / 7  = 0.0%
Medical-safety recall:   0 / 6  = 0.0%
Average routing latency: ~0.03 ms
Paid routing API cost:   $0
```

## Interpretation

The baseline is computationally cheap, but it is not usable for Ukrainian production traffic.

The main failure is not RAG quality. The request is often sent to the wrong route before the downstream RAG/workflow is executed.

## Decision

Use the HW7 English-keyword router only as the **before/baseline** reference.

---

# Experiment 002 — Strategy A: Native Ukrainian Rules

**Date:** 2026-09-02  
**Status:** Completed

## Change

Added:

```text
Ukrainian deterministic routing rules
+
shared deterministic medical-safety pre-gate
```

No paid model call is required for routing.

## Hypothesis

Native Ukrainian rules should provide a large improvement over the English-keyword baseline at almost zero incremental API cost.

## Measured result

```text
Routing accuracy:        11 / 13 = 84.6%
Real-user accuracy:       5 / 7  = 71.4%
Medical-safety recall:    4 / 6  = 66.7%
Average routing latency: ~0.07 ms
Input tokens:             0
Output tokens:            0
Paid routing API cost:    $0
```

## Improvement vs baseline

```text
Overall accuracy:
7.7% → 84.6%

Real-user accuracy:
0.0% → 71.4%

Medical-safety recall:
0.0% → 66.7%
```

## Remaining failures

### R06

User request:

```text
Сьогодні. Прокинулася, наче не боліло. Попрацювала, але одразу повернувся біль від сидіння...
```

Expected:

```text
back_pain_medical_request
```

Actual:

```text
health_psychology
```

Interpretation:

A long natural-language personal pain narrative is more difficult to classify reliably using simple lexical rules.

### R10

User request describes a proposed rehabilitation / stretching / exercise progression.

Expected:

```text
back_pain_medical_request
```

Actual:

```text
clarification
```

Interpretation:

The medical intent is implicit and distributed across a long colloquial request rather than expressed through one simple keyword.

## Decision

Strategy A is currently the strongest **overall accuracy / latency / API-cost** baseline.

However, it does not yet meet a strong enough medical-safety recall target for production use.

Do not declare Strategy A the production winner yet.

---

# Experiment 003 — Strategy B: Translate Then Route

**Date:** 2026-09-02  
**Status:** Invalid run — rerun required

## Intended strategy

```text
Ukrainian request
→ Gemini translation to English
→ English deterministic router
```

The shared deterministic medical-safety pre-gate runs before translation for obvious safety-sensitive requests.

## Hypothesis

Translation may normalize Ukrainian phrasing and allow reuse of an English routing layer, but it adds:

- an additional model call;
- tokens;
- API cost;
- latency;
- an additional failure point.

## Observed run

Reported benchmark values:

```text
Routing accuracy:        38.5%
Real-user accuracy:      57.1%
Medical-safety recall:   66.7%
Average latency:         ~324 ms
Input tokens:            0
Output tokens:           0
API cost:                $0
Errors:                  9
```

## Why this run is invalid

Nine translation calls returned:

```text
ClientError: 404 NOT_FOUND
```

Therefore the translation strategy did not execute successfully for most applicable cases.

The reported `38.5%` must **not** be interpreted as Strategy B routing accuracy.

A second evaluation issue was also identified:

```text
failed API call
→ fallback route = clarification
→ expected route may also equal clarification
→ evaluator could count the failed run as correct
```

This means execution success must be part of correctness.

## Fix required

Correctness should be:

```python
correct = (
    result.error is None
    and result.route == expected_route
)
```

## Decision

Do not compare Strategy B against A or C until:

```text
errors = 0
input_tokens > 0
output_tokens > 0
translation API cost > 0
```

**Next action:** rerun with an available translation model and corrected evaluator.

---

# Experiment 004 — Strategy C: Multilingual Semantic Embeddings

**Date:** 2026-09-02  
**Status:** Completed — needs tuning

## Strategy

```text
Ukrainian query
→ multilingual embedding
→ capability similarity
→ structured route
```

Model:

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

The deterministic medical-safety pre-gate remains outside the semantic router.

## Hypothesis

Semantic routing should handle Ukrainian paraphrases better than keyword rules, but will require more compute and threshold calibration.

## Measured result

```text
Routing accuracy:        9 / 13 = 69.2%
Real-user accuracy:      5 / 7  = 71.4%
Medical-safety recall:   5 / 6  = 83.3%
Average routing latency: ~32.3 ms
Paid API cost:           $0
```

Important:

```text
$0 API inference cost ≠ zero production cost
```

The local embedding model still consumes CPU/GPU resources and has a large model-download/runtime footprint.

## Comparison with Strategy A

```text
                         A Rules       C Semantic
Overall accuracy         84.6%         69.2%
Real-user accuracy       71.4%         71.4%
Medical-safety recall    66.7%         83.3%
Latency                  ~0.07 ms      ~32.3 ms
Paid API cost            $0            $0*
```

`*` Local infrastructure cost is not included.

## Important failures

### C02

```text
Що таке біопсихосоціальна модель здоров'я?
```

Expected:

```text
health_psychology
```

Actual:

```text
back_pain_medical_request
```

Confidence:

```text
0.526610
```

Interpretation:

Semantic similarity alone can over-associate domain concepts with the medical-safety capability.

### C06

```text
Чому я уникаю руху, коли боюся, що він посилить біль?
```

Expected:

```text
health_psychology
```

Actual:

```text
back_pain_medical_request
```

Interpretation:

The semantic router interprets first-person pain language as medical intent even when the request is conceptual Health Psychology.

### R02

```text
Ергономічний стул
```

Expected:

```text
health_psychology
```

Actual:

```text
clarification
```

Confidence:

```text
0.168637
```

Interpretation:

The capability descriptions / similarity threshold do not yet give sufficient semantic coverage for short ergonomics queries.

### R06

Long personal pain/work narrative.

Expected:

```text
back_pain_medical_request
```

Actual:

```text
clarification
```

Confidence:

```text
0.233250
```

Interpretation:

A generic capability embedding is not automatically sufficient for complex real-user narratives.

## Decision

Strategy C is **not automatically better because it is semantic**.

It currently improves medical-safety recall but loses overall routing accuracy and adds significant latency/compute compared with Strategy A.

Threshold and capability representations require calibration.

---

# Experiment 005 — Conversation & Funnel Observability

**Date:** 2026-09-02  
**Status:** Implemented, production data not yet available

## Goal

Connect routing and AI cost to the eventual IVR business funnel.

## Added conversation state

The system can track:

```text
turn_count
domain_turn_count
unique_topic_count
risk_level
medical_safety_triggered
professional_care_required
location_permission
confirmed_city
IVR CTA state
LLM calls
input tokens
output tokens
estimated AI cost
```

## Funnel events

```text
conversation_started
→ domain_engaged
→ soft_cta_eligible
→ ivr_cta_shown
→ ivr_cta_accepted
→ clinic_discussion_started
→ ivr_link_clicked
→ booking_started
→ booking_completed
```

## CTA policy

Low / moderate risk:

```text
turn 1–5
→ useful evidence-grounded conversation

turn >= 6
AND sufficient domain engagement
→ soft IVR CTA eligible
```

High risk:

```text
professional-care pathway immediately
```

Safety is not delayed for conversion optimization.

## Future business metrics

Once real traffic and booking events exist:

```text
AI cost per conversation
AI cost per IVR CTA acceptance
AI cost per IVR website click
AI cost per booking
```

Ultimately:

```text
AI-assisted acquisition cost
vs
CAC from other acquisition channels
```

## Current limitation

No real IVR conversion data is available yet.

Therefore the project instruments these metrics but does not report invented conversion results.

---

# Architecture Decision 001 — Do Not Use One Expensive Router for Every Request

**Status:** Working hypothesis

Current evidence suggests that neither pure rules nor pure semantic routing dominates all metrics.

Observed trade-off:

```text
Native rules:
best overall accuracy
very low latency
lower medical-safety recall

Semantic router:
better medical-safety recall
lower overall accuracy
higher compute/latency
```

A promising future architecture is therefore:

```text
deterministic medical-safety pre-gate
↓
cheap Ukrainian router
↓
high confidence?
├─ yes → execute route
└─ no  → semantic fallback
```

This would use expensive semantic reasoning only where it may add value.

**Important:** this architecture has not yet been evaluated and is not presented as a measured final result.

---

# Experiment Template

Copy this section for every new run.

## Experiment XXX — <name>

**Date:** YYYY-MM-DD  
**Status:** Planned / Running / Completed / Invalid

### Question

What exactly are we trying to learn?

### Hypothesis

What do we expect and why?

### Change

What code, prompt, model, threshold, dataset or policy changed?

### Dataset

```text
cases:
slices:
version:
```

### Configuration

```text
model:
threshold:
routing policy:
pricing assumption:
other:
```

### Metrics

```text
routing_accuracy:
real_user_accuracy:
medical_safety_recall:
avg_latency_ms:
input_tokens:
output_tokens:
estimated_api_cost_usd:
cost_per_correct_route_usd:
errors:
```

### Failures / examples

Record concrete cases, not only averages.

### Interpretation

What did the run actually teach us?

### Decision

Keep / revert / modify / investigate.

### Next step

One concrete next experiment.

---

# Current Project Status

As of 2026-09-02:

```text
Baseline                measured
Strategy A              measured
Strategy B              invalid — rerun required
Strategy C              measured
Conversation state      implemented
Funnel instrumentation  implemented
Location consent demo   implemented
Final production router not selected yet
```

## Current strongest finding

The final routing decision cannot be made from sophistication alone.

The current data shows a real trade-off between:

```text
accuracy
medical-safety recall
latency
tokens / compute
cost
```

The production strategy should be selected only after Strategy B is rerun successfully and the evaluation set is expanded.
