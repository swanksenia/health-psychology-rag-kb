# Final Project Architecture Card

## Name

**IVR Health Psychology & Chronic Back Pain Domain-Specific Expert Assistant**

Final improvement:

**Multidimensional Ukrainian Routing with Safety Policy Overlay**

## Business use case

A Ukrainian-speaking user can start with a natural-language question about Health Psychology, chronic or back pain, work discomfort, medication, exercise, or related concerns.

The assistant should:
- understand the request in Ukrainian;
- identify intent, context and risk;
- select the preferred capability;
- apply required safety or authorization policies;
- provide evidence-grounded psychoeducation when appropriate;
- move to a professional-care pathway when required;
- avoid unnecessary LLM calls and AI cost.

## Target user

Ukrainian-speaking IVR prospects / users seeking:
- Health Psychology psychoeducation;
- help understanding chronic-pain-related behaviour and functioning;
- safe navigation when a personal medical question requires professional assessment.

## Existing data & integrations

Existing project:
- Health Psychology scientific knowledge base;
- FAISS semantic retrieval;
- RAG answer generation;
- IVR structured care information;
- product analytics tool;
- LangGraph orchestration;
- evaluation and observability.

Final-project additions:
- Ukrainian routing evaluation set;
- anonymized real-user-derived evaluation slice;
- multilingual routing experiments;
- multidimensional Taxonomy v2;
- safety and authorization policy overlay;
- conversation and funnel observability;
- token and estimated AI-cost tracking;
- retrieval runtime caching.

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
Trace + conversation + funnel metrics
```

Medical safety is a policy overlay rather than a competing topic.

A request can therefore preserve a Health Psychology response context while also activating medical-safety restrictions.

## Why not multi-agent

The system remains one domain-specific assistant with specialized workflows.

Multiple autonomous agents would add:
- extra model calls;
- latency;
- state complexity;
- more difficult evaluation;
- cost without a demonstrated benefit for this scope.

## Guardrails

- no diagnosis;
- no medication dosing or recommendation;
- no individualized exercise prescription;
- no individualized treatment prescription;
- medical-safety policy is applied deterministically;
- trusted backend role controls analytics access;
- high-risk requests enter the professional-care pathway immediately;
- location-dependent requests require user permission and city confirmation;
- precise coordinates are not persisted by the demo.

## Quality criteria

Routing and policy quality:
- preferred-capability accuracy;
- allowed-capability accuracy;
- risk-class accuracy;
- required-policy accuracy;
- medical-safety recall;
- unsafe-route rate;
- clarification appropriateness.

Knowledge quality:
- retrieval relevance;
- grounded synthesis;
- knowledge coverage;
- explicit insufficient-evidence handling.

Efficiency:
- retrieval latency;
- LLM latency;
- tokens;
- LLM calls;
- estimated AI cost.

Conversation:
- turns;
- domain engagement;
- risk state;
- LLM calls;
- estimated cost.

Future business:
- IVR CTA acceptance;
- site click;
- booking;
- AI cost per booked consultation.

## Observability and runtime optimization

Conversation-level traces record:

```text
taxonomy classification
retrieval
LLM synthesis
provider
model
prompt version
tokens
latency
estimated cost
success / error
```

Observability exposed repeated retrieval initialization as a latency bottleneck.

After caching the embedding model, FAISS index and retrieval chunks:

```text
cold retrieval latency:         5456.57 ms
warm cached retrieval latency:   459.48 ms
warm-cache speedup:              ~11.9×
```

This is a local benchmark and should not be interpreted as production latency.

## Final-project additions

- multidimensional Ukrainian routing taxonomy;
- preferred capability + required policy separation;
- deterministic medical-safety overlay;
- Taxonomy v2 evaluation contract;
- Health Psychology RAG integration;
- Claude grounded synthesis;
- deterministic IVR care navigation;
- conversation and funnel observability;
- provider/model/token/cost tracing;
- cached retrieval runtime.

## Out of scope for final-project demo

- production CRM;
- live appointment availability;
- real booking integration;
- clinical diagnosis;
- personalized treatment;
- production geolocation backend;
- production CAC comparison;
- production conversion metrics;
- comprehensive pharmacological or neurological knowledge coverage;
- multilingual code-switching beyond the current Ukrainian evaluation set.