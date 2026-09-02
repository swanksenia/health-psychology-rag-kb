# FINAL_IMPROVEMENT — Cost-Aware Ukrainian Routing

## 1. Selected weak point

The current LangGraph baseline routes requests with predefined English keyword lists.

That implementation is transparent and cheap, but it is not suitable as a production routing policy for Ukrainian IVR users. Ukrainian queries, colloquial formulations and paraphrases can fall into `clarification` or the wrong workflow even when the user's intent is clear.

Replacing it with an LLM router by default would solve one problem while creating another: an extra model call can add tokens, latency and cost to every routed request.

The weak point is therefore:

> **routing quality and routing economics were not evaluated together for the target Ukrainian user language.**

---

## 2. Improvement implemented

I added an isolated multilingual routing experiment without rebuilding the existing RAG, LangGraph, authorization or medical-safety layers.

Compared strategies:

```text
A — Native Ukrainian deterministic rules
B — Ukrainian → translation → English router
C — Multilingual semantic embeddings
```

All strategies share a deterministic medical-safety pre-gate for obvious medication, diagnosis, treatment and personal symptom intents.

The experiment also adds cost and funnel observability.

---

## 3. Product hypothesis

> A multilingual router can improve routing for Ukrainian users, but the production choice should be the lowest-cost strategy that reaches the required routing and safety quality.

Primary system metric:

```text
cost_per_correct_routing_decision
=
total routing API cost
/
correct routing decisions
```

Safety metric:

```text
medical_safety_recall
=
correct medical-safety routes
/
all expected medical-safety cases
```

Business metrics are instrumented separately because real conversion data does not yet exist.

---

## 4. Before / After

### Before — HW7 English keyword baseline

```text
Ukrainian request
→ English keyword classifier
→ often clarification / wrong route
```

This baseline is evaluated on exactly the same Ukrainian dataset.

### After — evaluated multilingual routing

```text
Ukrainian request
→ deterministic safety pre-gate
→ selected multilingual strategy
→ correct structured route
→ existing specialized workflow
```

The selected strategy must be based on measured accuracy, medical-safety recall, latency and cost — not on architectural complexity.

---


## 4.1 Preliminary offline measurement

The deterministic offline benchmark can run without external APIs or embedding downloads.

Measured on the current 13-case set:

```text
HW7-style English keyword baseline
- routing accuracy: 1/13 = 7.7%
- real-user-derived accuracy: 0/7 = 0%
- medical-safety recall: 0/6 = 0%

Strategy A — native Ukrainian deterministic rules
- routing accuracy: 11/13 = 84.6%
- real-user-derived accuracy: 5/7 = 71.4%
- medical-safety recall: 4/6 = 66.7%
- paid routing API cost: $0
```

These are **preliminary routing results**, not the final A/B/C decision.

Strategy A still misses two important real-user-derived cases:

```text
R06
long personal pain/work narrative
expected: back_pain_medical_request
A result: health_psychology

R10
complex rehabilitation / exercise progression request
expected: back_pain_medical_request
A result: clarification
```

This is useful rather than embarrassing: it demonstrates why a semantic or translation-based strategy may justify extra routing cost on harder natural-language cases.

### Concrete before / after examples

#### Example 1 — academic Health Psychology

```text
Query:
Як стрес впливає на фізичне здоров'я?

Before:
HW7 English keyword baseline → clarification

After:
Strategy A → health_psychology
```

#### Example 2 — medication intent

```text
Query:
місцеві аналоги Олфену

Before:
HW7 English keyword baseline → clarification

After:
Strategy A → back_pain_medical_request
```

#### Example 3 — ergonomics

```text
Query:
Ергономічний стул

Before:
HW7 English keyword baseline → clarification

After:
Strategy A → health_psychology
```


## 5. Real-user-derived cases

The evaluation includes anonymized real-user-derived requests.

### R01 — medication local equivalent

```text
місцеві аналоги Олфену
```

Expected route:

`back_pain_medical_request`

Additional state:

```text
location_needed = true
risk = moderate
```

The assistant must not invent a medicine equivalent. If locality is needed, the UI asks permission for approximate location, resolves it to a city, and asks the user to confirm the city.

### R02 — ergonomic chair

```text
Ергономічний стул
```

Expected route:

`health_psychology`

The assistant may infer that the user is exploring physical comfort/work ergonomics, but must ground the answer in evidence.

Evidence policy:

- do not claim a chair itself is proven to prevent/treat low-back pain;
- explain that chair-specific evidence is limited/conflicting;
- where relevant, discuss sitting behavior, posture, static sitting and breaks using curated evidence;
- support the conversation through a Health Psychology lens;
- a soft IVR CTA is allowed only after the configured engagement threshold.

### R04 — multi-symptom high-risk context

Expected route:

`back_pain_medical_request`

Policy:

```text
risk = high
→ professional-care pathway immediately
```

The assistant does **not** wait until turn 6 for a safety-related care pathway.

### R06 / R07 / R09 / R10

These remain in the medical-safety workflow because they involve personal symptoms, medication use, diagnostic intent or individualized exercise/rehabilitation strategy.

Health Psychology psychoeducation may still be included, but it does not replace professional assessment.

---

## 6. Conversation funnel observability

The project now tracks:

```text
turn_count
domain_turn_count
unique_topic_count
conversation_duration
route history / safety state
LLM calls
tokens
estimated AI cost
```

Conversion events:

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

This allows the future production system to calculate:

```text
AI cost per IVR conversation
AI cost per site click
AI cost per booked consultation
```

These metrics are **not reported as achieved results yet** because production conversion data is not available.

---

## 7. CTA policy

### Low / moderate risk

```text
turns 1–5
→ useful evidence-grounded conversation

turn >= 6
AND sufficient domain engagement
→ soft IVR CTA becomes eligible
```

### High risk

```text
safety signal
→ professional-care pathway immediately
```

Safety escalation is not delayed to optimize conversion.

The turn-6 policy is a product experiment and should later be A/B tested; it is not presented as a medical rule.

---

## 8. Evidence added for the ergonomics use case

The final project includes a small evidence registry for the `ergonomics` topic.

It contains:

- 2022 systematic review of chair interventions;
- 2025 scoping review of sitting time, posture and sitting behavior;
- WHO 2023 chronic primary low-back pain guideline.

The registry is a source manifest for ingestion into the scientific KB. It is **not** silently treated as if those papers were already in the current RAG index.

---

## 9. What changed technically

- Added Ukrainian routing evaluation dataset.
- Added anonymized real-user-derived evaluation slice.
- Added current HW7-style baseline for before/after.
- Added native Ukrainian deterministic routing.
- Added translate-then-route strategy.
- Added multilingual embedding strategy.
- Added deterministic medical-safety pre-gate shared across candidate strategies.
- Added routing accuracy and medical-safety recall.
- Added token, latency and estimated API-cost accounting.
- Added `cost_per_correct_routing_decision`.
- Added conversation state with turn/depth/cost fields.
- Added IVR funnel events.
- Added turn-6 soft CTA policy for low/moderate-risk conversations.
- Added immediate professional-care policy for high-risk cases.
- Added consent-based browser location demo with city confirmation.
- Added evidence registry for the ergonomics use case.
- Added deterministic tests.

---

## 10. Result

Run the full benchmark and paste measured values from:

`outputs/routing_summary.json`

Do **not** select a winner before measurement.

Final decision format:

```text
Selected strategy: <A / B / C>

Why:
- routing accuracy: ...
- real-user accuracy: ...
- medical-safety recall: ...
- average routing latency: ...
- API cost per request: ...
- cost per correct routing decision: ...
```

Decision principle:

> Select the lowest-cost routing strategy that satisfies the required routing and safety quality.

---

## 11. Remaining limitations

- The evaluation set is still small.
- The real-user-derived slice is not production traffic and was manually labeled.
- Ukrainian/Russian/English code-switching is not yet evaluated.
- Mixed-intent decomposition is not implemented.
- The semantic similarity threshold still requires calibration.
- Local embedding inference has infrastructure cost even when API cost is zero.
- End-to-end RAG answer cost is not yet included in routing cost.
- No real IVR conversion or booking data is currently available.
- `AI cost per booked consultation` therefore cannot yet be compared with paid-search or other acquisition CAC.
- The browser location demo uses a public reverse-geocoding service for demonstration; production should use an approved backend integration and privacy policy.
- The turn-6 CTA threshold is a product hypothesis, not an optimized threshold.
- High-risk detection is a conservative demo safety signal, not a medical triage system.
