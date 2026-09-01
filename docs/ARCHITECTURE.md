# Target Architecture

## Health Psychology Domain-Specific AI Platform

The final project evolves the existing Health Psychology RAG assistant into a domain-specific AI platform with three specialized capabilities:

1. Domain-Specific Expert Assistant;
2. Analytics / Text2SQL Assistant;
3. Customer Support and Clinic Booking Assistant.

The system uses one orchestration layer with specialized workflows rather than several autonomous agents.

Different capabilities may use different LLM models and even different vendors.

---

# 1. High-Level Architecture

```text
                         User Request
                              ↓
                        Request Context
                              ↓
                    RAG-Assisted Controller
                              ↓
                     Capability Retrieval
                              ↓
                   Structured Route Decision
                              ↓
          ┌───────────────────┼───────────────────┐
          ↓                   ↓                   ↓
   Domain Expert        Analytics / Text2SQL   Customer Support
          ↓                   ↓                   ↓
   Scientific RAG       Schema / Metrics        Clinic RAG
          ↓              Retrieval                 ↓
   Safety Rules              ↓                 Live Tools
          ↓               Text2SQL                 ↓
   Expert Model              ↓                Support Model
                         Validation
                              ↓
                        Read-Only Data
          └───────────────────┼───────────────────┘
                              ↓
                         Final Answer
                              ↓
                     Trace + Evaluation
```

---

# 2. Domain-Specific Expert Assistant

This capability handles Health Psychology and psychoeducational questions.

Typical requests include:

- Health Psychology concepts;
- chronic pain psychology;
- stress and health;
- behaviour change;
- scientific evidence interpretation;
- comparison and synthesis across several sources.

Workflow:

```text
User Question
↓
Capability Routing
↓
Scientific Knowledge RAG
↓
Relevant Evidence
↓
Domain Rules
↓
Medical Safety Boundary
↓
Expert Model
↓
Grounded Answer with Citations
```

Simple domain questions may use a faster and cheaper model.

Complex questions that require synthesis across multiple sources may be escalated to a stronger reasoning model.

---

# 3. Analytics / Text2SQL Assistant

This capability handles questions about structured product and business data.

Workflow:

```text
User Question
↓
Analytics Intent
↓
Authorization
↓
Metric / Schema Retrieval
↓
Query Generation
↓
Query Validation
↓
Read-Only Execution
↓
Result
↓
Natural-Language Explanation
```

The LLM should not perform trusted business calculations itself.

SQL, Python, APIs, or analytical databases should perform deterministic computation.

The LLM is mainly responsible for:

- understanding analytical intent;
- selecting relevant metrics;
- generating structured queries;
- explaining results.

---

# 4. Customer Support and Clinic Booking Assistant

This capability handles clinic information and appointment workflows.

Typical requests include:

- services;
- prices;
- doctors;
- specializations;
- clinic locations;
- online consultations;
- available appointment slots;
- booking;
- rescheduling;
- cancellation.

Workflow:

```text
Customer Request
↓
Customer Support Workflow
↓
Clinic RAG
+
Live Clinic Tools
↓
Confirmation
↓
Answer / Action
```

Possible tools include:

```text
search_services()
search_doctors()
search_locations()
get_available_slots()
create_booking()
reschedule_booking()
cancel_booking()
```

Write actions such as creating or changing an appointment require explicit user confirmation.

---

# 5. Medical Safety Boundary

Customer Support must not become an uncontrolled diagnostic system.

Example:

```text
"Find a neurologist in Lviv."
```

can go directly to Customer Support.

But:

```text
"My leg is numb and my lower back hurts.
Which doctor should I see?"
```

contains a medical interpretation component.

The expected flow is:

```text
Medical Safety Workflow
↓
Safe Next-Step Guidance
↓
Customer Support
↓
Doctor / Location / Appointment Search
```

Medical safety rules remain explicit and deterministic.

---

# 6. RAG-Assisted Controller

The controller evolves from the current HW7 keyword classifier toward semantic capability routing.

Routing RAG answers:

> Which capability or workflow should handle this request?

Its knowledge base can contain:

- capability descriptions;
- routing policies;
- positive examples;
- negative examples;
- tool requirements;
- safety constraints.

Routing retrieval retrieves workflow knowledge, not scientific answers.

---

# 7. Separate Retrieval Layers

The architecture separates different retrieval responsibilities.

## Routing Retrieval

Purpose:

> Which workflow should handle the request?

Retrieves:

- capabilities;
- workflow descriptions;
- routing policies;
- examples.

## Scientific Knowledge Retrieval

Purpose:

> What scientific evidence is required for the answer?

Retrieves:

- scientific papers;
- course materials;
- textbooks;
- domain documents.

## Analytics Retrieval

Purpose:

> How should the analytics request be translated into a valid query?

Retrieves:

- schemas;
- metrics;
- business definitions;
- relationships;
- query examples.

## Clinic Retrieval

Purpose:

> What clinic information is relevant to the support request?

Retrieves:

- services;
- doctors;
- specializations;
- locations;
- FAQ;
- policies.

---

# 8. Model-Agnostic LLM Layer

The application should not depend directly on a single LLM vendor.

```text
                    Application
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
        Router        Workflows      Evaluator
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                  LLM Provider Layer
                         ↓
             ┌───────────┼───────────┐
             ↓           ↓           ↓
          OpenAI      Anthropic     Azure
```

Application code should use an internal provider interface instead of embedding vendor-specific APIs throughout the workflow.

This allows models and vendors to be changed without rewriting the orchestration logic.

---

# 9. Specialized Model Profiles

## Router

Priority:

- low latency;
- low cost;
- reliable structured output;
- reliable routing.

## Domain Expert

Priority:

- strong reasoning;
- grounded synthesis;
- instruction following;
- citation quality.

## Analytics / Text2SQL

Priority:

- structured output;
- SQL reasoning;
- schema understanding;
- reliable tool use.

## Customer Support

Priority:

- low latency;
- low cost;
- conversation quality;
- reliable tool calling.

## Evaluator

The evaluator may use a different model or vendor from the production workflow.

---

# 10. Model Escalation

The strongest model should not be used for every request.

```text
Simple Request
↓
Fast / Lower-Cost Model

Complex Domain Synthesis
↓
Strong Reasoning Model

High-Risk or High-Uncertainty Request
↓
Strong Reasoning Model
+
Safety Workflow
+
Human Escalation if Required
```

---

# 11. Deterministic Policy Gates

Some decisions should not be delegated to semantic retrieval or LLM reasoning.

Examples:

```text
Authorization
→ trusted backend role

Medical Safety
→ deterministic safety policy

Analytics
→ read-only database access

Booking
→ explicit user confirmation
```

Semantic reasoning helps understand the request.

Deterministic rules control sensitive actions.

---

# 12. Orchestration Runtime

LangGraph remains the orchestration runtime.

It provides:

- explicit state;
- nodes;
- edges;
- conditional routing;
- controlled workflow transitions;
- execution traces.

The target system therefore uses:

> one controller with several specialized workflows.

---

# 13. Observability

Each execution should expose a trace such as:

```text
User Request
↓
Capabilities Retrieved
↓
Selected Route
↓
Policy Decision
↓
Retrieved Evidence / Schema
↓
Tools Called
↓
Model Selected
↓
Final Answer
```

Runtime metadata should eventually include:

- provider;
- model;
- input tokens;
- output tokens;
- latency;
- estimated cost;
- route;
- tool calls;
- retrieved sources;
- errors.

This supports quality evaluation, debugging, and economics analysis.

---

# 14. Design Principles

The target architecture follows four main principles:

1. use semantic reasoning where semantic reasoning adds value;
2. use deterministic controls where deterministic rules are possible;
3. use specialized models and workflows instead of one model for every task;
4. keep the core application provider-independent.

The goal is not maximum agent autonomy.

The goal is a controllable and observable domain-specific AI system whose quality, safety, latency, and cost can be measured.
