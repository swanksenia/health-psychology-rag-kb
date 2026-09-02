# Final Project Architecture Card

## Name

**IVR Health Psychology & Chronic Back Pain Domain-Specific Expert Assistant**

Final improvement:

**Cost-Aware Ukrainian Routing**

## Business use case

A Ukrainian-speaking user can start with a natural-language question about health psychology, chronic/back pain, work discomfort, medication, exercise, or related concerns.

The assistant should:
- understand the request in Ukrainian;
- send it to the correct workflow;
- preserve deterministic medical-safety and authorization boundaries;
- provide evidence-grounded psychoeducation when appropriate;
- move to a professional-care pathway when appropriate;
- avoid unnecessary AI cost.

## Target user

Ukrainian-speaking IVR prospects / users seeking:
- Health Psychology psychoeducation;
- help understanding chronic-pain-related behavior and functioning;
- safe navigation when a personal medical question requires professional assessment.

## Existing data & integrations

Existing project:
- Health Psychology scientific knowledge base;
- semantic / improved retrieval;
- RAG answer generation;
- IVR structured care information;
- product analytics tool;
- LangGraph orchestration;
- evaluation / observability.

Final-project additions:
- Ukrainian routing eval set;
- real-user-derived eval slice;
- multilingual routing candidates;
- cost metrics;
- conversation/funnel event state;
- small ergonomics evidence registry.

## Architecture

```text
User
↓
Deterministic medical-safety pre-gate
↓
Cost-aware multilingual routing
↓
Structured route
↓
Deterministic policy gate
↓
Existing workflow / Knowledge RAG / tool
↓
Grounded answer
↓
Trace + conversation + funnel metrics
```

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
- no medication recommendation;
- no individualized exercise prescription;
- no treatment prescription;
- trusted backend role controls analytics access;
- high-risk safety pathway does not wait for a conversion threshold;
- location requires user permission and city confirmation;
- precise coordinates are not persisted by the demo.

## Quality criteria

Routing:
- routing accuracy;
- real-user accuracy;
- medical-safety recall;
- latency;
- tokens;
- API cost;
- cost per correct routing decision.

Conversation:
- turns;
- domain turns;
- unique topics;
- LLM calls;
- tokens;
- estimated cost.

Future business:
- IVR CTA acceptance;
- clinic discussion;
- site click;
- booking;
- AI cost per booked consultation.

## Out of scope for final-project demo

- production CRM;
- live appointment availability;
- real booking integration;
- clinical diagnosis;
- personalized treatment;
- production geolocation backend;
- production CAC comparison;
- multilingual code-switching beyond current Ukrainian test set.
