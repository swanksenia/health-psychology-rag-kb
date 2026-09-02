# Final Project — Cost-Aware Ukrainian Routing & Conversation Funnel

## Product

**IVR Health Psychology & Chronic Back Pain Domain-Specific Expert Assistant**

This final project extends the existing course project without rebuilding its RAG, safety, tool or LangGraph layers.

The focused technical improvement is:

> **replace the English keyword-routing baseline with an evaluated Ukrainian/multilingual routing strategy, and measure routing quality together with serving cost.**

The conversation funnel is added as an **observability layer** so routing quality can later be connected to business outcomes such as IVR conversation, website click and booking.

---

## Why this is a product problem

A more advanced router is not automatically a better product.

For IVR, the relevant question is:

> Which routing strategy gives the lowest cost per correct and safe routing decision for Ukrainian users?

A router that is cheap but wrong can send users into the wrong workflow.
A router that is accurate but adds an unnecessary model call to every turn can make the product economically unattractive.

---

## Architecture

```text
User request
    ↓
Shared deterministic safety pre-gate
    ↓
Routing strategy
    ├─ A: native Ukrainian rules
    ├─ B: translate → English router
    └─ C: multilingual semantic router
    ↓
Structured route
    ↓
Existing deterministic authorization / medical policy gates
    ↓
Existing specialized workflow / Knowledge RAG / tool
    ↓
Grounded answer
    ↓
Conversation + cost observability
```

The existing HW8 design principle is preserved:

```text
semantic reasoning where useful
+
deterministic controls where possible
```

---

## Strategies

### Baseline — current HW7-style English keywords

Used only as the **before** reference.

### Strategy A — Native Ukrainian deterministic router

- deterministic;
- no paid model call;
- very low latency;
- needs rule maintenance;
- can miss unseen paraphrases.

### Strategy B — Translate then route

```text
Ukrainian
→ Gemini 2.5 Flash-Lite translation
→ English deterministic router
```

The shared medical-safety pre-gate runs **before translation**, so obvious medical requests do not pay for translation.

### Strategy C — Multilingual semantic router

```text
Ukrainian
→ multilingual embedding
→ capability similarity
→ route
```

Model:

`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

It has no per-request model API charge in this demo, but local CPU/GPU infrastructure cost is not zero.

---

## Real-user-derived test slice

The evaluation includes anonymized real-user-derived Ukrainian queries such as:

- local equivalent of a medication;
- ergonomic chair;
- multi-symptom work/pain question;
- medication + exercise question;
- colloquial diagnostic intent;
- rehabilitation/exercise progression.

This slice is reported separately from controlled test cases.

---

## Safety policy

Safety is not optimized for conversion.

```text
high risk
→ professional-care pathway immediately

low/moderate risk
→ useful grounded conversation
→ soft IVR CTA only from turn 6
```

The "turn 6" rule is a **demo product policy**, not a clinical rule.

The assistant does not provide:

- diagnosis;
- medication recommendations;
- individualized exercise prescription;
- treatment prescription.

---

## Location handling

Location is requested only for use cases that genuinely require locality, e.g. a query about local availability.

Flow:

```text
location needed
→ ask user permission
→ browser geolocation prompt
→ reverse geocode to approximate city
→ ask "Схоже, ви зараз у <city>. Правильно?"
→ store only confirmed city
```

Precise coordinates are not persisted by this demo.

A browser demo is included in:

`web/location_consent_demo.html`

---

## Evidence policy for "Ергономічний стул"

The bot must not claim that an ergonomic chair itself is proven to prevent or treat low-back pain.

The included evidence registry documents:

1. a 2022 systematic review of chair interventions reporting very-low- to low-quality and conflicting evidence;
2. a 2025 scoping review reporting stronger associations for sitting behavior, including static sitting and fewer breaks;
3. WHO's 2023 chronic primary low-back pain guideline supporting holistic, person-centred management.

See:

`config/evidence_registry.json`

This evidence should be added to the scientific KB before the chatbot uses it as an answer source.

---

## Evaluation metrics

Routing:

- routing accuracy;
- real-user-derived routing accuracy;
- medical-safety recall;
- latency;
- tokens;
- API cost;
- **cost per correct routing decision**.

Conversation:

- `turn_count`;
- `domain_turn_count`;
- `unique_topic_count`;
- `conversation_duration_seconds`;
- `llm_calls`;
- tokens;
- estimated AI cost.

Funnel:

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

Future production KPI:

```text
AI cost per booked consultation
```

The project does **not** claim this metric yet because no production IVR conversion data is available.

---

## Run

### Fast offline checks

No API key or embedding model required:

```bash
python scripts/evaluate_offline.py
pytest -q
```

### Full A/B/C benchmark

```bash
pip install -r requirements.txt
export GEMINI_API_KEY="..."
python scripts/multilingual_router.py
```

Outputs are written to:

```text
outputs/routing_results.jsonl
outputs/routing_summary.json
```

---

## Decision rule

Do not select the most sophisticated router.

Select:

> **the lowest-cost strategy that passes the required routing quality and medical-safety threshold.**

The threshold itself must be calibrated on a larger pre-production evaluation set before launch.
