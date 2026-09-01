# AI Economics

This document defines how the project will measure and compare the economics of different AI workflows, models, and providers.

The goal is not only to understand token cost.

The main product question is:

> How much does one successful user task cost?

The project therefore evaluates cost together with:

```text
quality
+
task success
+
latency
+
reliability
```

---

# 1. Why Economics Is Part of the Architecture

The target system contains several different AI capabilities:

1. Domain-Specific Expert Assistant;
2. Analytics / Text2SQL Assistant;
3. Customer Support and Clinic Booking Assistant;
4. Router / Controller;
5. Evaluation layer.

These workflows have different requirements.

For example:

```text
Router
→ high volume
→ low latency
→ low cost
```

```text
Domain Expert
→ lower volume
→ higher reasoning requirements
→ potentially higher model cost
```

```text
Customer Support
→ high interaction frequency
→ low latency
→ strong cost sensitivity
```

For this reason, one model should not automatically be used for all workflows.

---

# 2. Runtime Cost Data

Each model run should eventually capture:

```text
workflow
route
provider
model
input_tokens
output_tokens
total_tokens
model_calls
latency_ms
retrieval_calls
tool_calls
estimated_llm_cost
estimated_tool_cost
total_estimated_cost
task_success
```

Where possible, cost data should be stored at the individual run level.

This makes it possible to compare:

```text
model cost
vs
workflow cost
vs
successful-task cost
```

---

# 3. Cost by Capability

Economics should be calculated separately for each capability.

## Router / Controller

Track:

- number of routing calls;
- average routing cost;
- latency;
- routing accuracy;
- cost per correctly routed request.

## Domain-Specific Expert

Track:

- retrieval cost;
- model cost;
- number of retrieved chunks;
- number of model calls;
- model escalation;
- groundedness;
- task success;
- cost per successful expert answer.

## Analytics / Text2SQL

Track:

- schema retrieval;
- model calls;
- SQL generation;
- validation;
- query execution;
- task success;
- cost per correct analytics answer.

## Customer Support

Track:

- model calls;
- RAG calls;
- tool calls;
- booking actions;
- task success;
- cost per successful support task;
- cost per successful booking.

## Evaluation

Track:

- deterministic evaluation cost;
- LLM-as-a-judge calls;
- evaluator provider;
- evaluator model;
- cost per evaluated case.

---

# 4. Core Economics Metrics

## Cost per Request

```text
total AI cost
/
total requests
```

This metric is useful for basic operational forecasting.

However, it is not sufficient on its own.

---

## Cost per Successful Task

```text
total AI cost
/
successful tasks
```

This is one of the primary product metrics.

A cheaper model may have a lower cost per request but a higher cost per successful task if it fails more often.

---

## Cost per Workflow

```text
total workflow cost
/
workflow executions
```

Examples:

```text
Domain Expert cost per request

Analytics cost per request

Customer Support cost per request
```

---

## Cost per Successful Booking

For the Customer Support workflow:

```text
total Customer Support AI cost
/
successful bookings
```

This can later be connected to business funnel metrics.

---

## Cost per Correct Analytics Answer

For Analytics / Text2SQL:

```text
total Analytics AI cost
/
correct analytics tasks
```

---

## Cost per Grounded Expert Answer

For the Domain Expert:

```text
total Domain Expert AI cost
/
successful grounded answers
```

---

# 5. Model Escalation Economics

The system should not automatically use a high-cost reasoning model for every Domain Expert request.

A possible architecture is:

```text
Simple Question
↓
Standard / Lower-Cost Model
```

```text
Complex Question
↓
Strong Reasoning Model
```

The system should record:

```text
initial_model
escalation_triggered
escalated_model
additional_cost
final_task_success
```

---

## Model Escalation Rate

```text
requests escalated to a stronger model
/
total eligible requests
```

This helps determine whether the escalation policy is selective enough.

---

## Escalation Value

The system should evaluate whether additional model cost actually improves quality.

Example comparison:

```text
Standard Model

cost = lower
task success = 80%
```

versus:

```text
Reasoning Model

cost = higher
task success = 95%
```

The relevant product question is:

> Is the additional quality worth the additional cost for this workflow?

---

# 6. Multi-Provider Cost Comparison

The model-agnostic architecture allows the same workflow to be tested across different providers.

Possible comparison:

```text
Same Use Case
+
Same Retrieval
+
Same Retrieved Evidence
+
Same Prompt
+
Same Evaluation
↓
OpenAI
vs
Anthropic
vs
Azure-hosted model
```

The experiment should measure:

- task success;
- groundedness;
- answer quality;
- latency;
- input tokens;
- output tokens;
- estimated cost.

The goal is not to identify one universally best provider.

The goal is to identify the best provider/model trade-off for each capability.

---

# 7. Quality–Cost Trade-Off

Models should not be selected only by price.

Evaluation should consider:

```text
Quality
↑

Cost
↓

Latency
↓

Reliability
↑
```

A lower-cost model is not necessarily better if:

- routing accuracy becomes worse;
- SQL correctness decreases;
- groundedness decreases;
- booking workflow fails more often.

A stronger model is also not automatically better if a cheaper model produces equivalent task success.

---

# 8. Retrieval Economics

RAG cost should also be included in the workflow economics.

Relevant factors include:

- embedding generation;
- number of retrieval calls;
- number of retrieved chunks;
- context size;
- reranking calls;
- additional model calls.

Potential optimization strategies include:

```text
smaller retrieval context
↓
fewer input tokens
↓
lower generation cost
```

but context should not be reduced if retrieval quality or groundedness becomes worse.

---

# 9. Tool Economics

Tools may also have operational costs.

Examples include:

```text
database query
external API
booking API
search API
reranker API
```

The project should distinguish:

```text
LLM cost
+
retrieval cost
+
tool cost
=
total workflow cost
```

For the current educational implementation, some tools are local and therefore have no external API cost.

Future production integrations may introduce additional costs.

---

# 10. Deterministic Logic as Cost Optimization

Not every task should require an LLM call.

Examples:

```text
authorization
→ deterministic
```

```text
SQL validation
→ deterministic
```

```text
exact arithmetic
→ deterministic
```

```text
booking confirmation check
→ deterministic
```

```text
basic evaluation assertions
→ deterministic
```

Using deterministic logic where possible can improve:

- reliability;
- latency;
- cost.

---

# 11. Caching Opportunities

Potential caching strategies include:

## Embedding Cache

Avoid recalculating embeddings for unchanged documents.

## Retrieval Cache

Cache results for repeated stable queries where appropriate.

## Static Clinic Knowledge Cache

Cache relatively stable clinic information.

## Model Response Cache

Use only where the request, context, permissions, and safety conditions make caching appropriate.

Dynamic information such as:

```text
appointment availability
```

should not rely on stale cache when live data is required.

---

# 12. Cost Observability

Cost should be part of the execution trace.

Example trace:

```text
User Request
↓
Route
↓
Retrieval
↓
Model Call
↓
Tool Calls
↓
Final Answer
↓
Task Success
↓
Cost Record
```

The trace should eventually include:

```text
provider
model
input_tokens
output_tokens
model_calls
latency_ms
retrieval_calls
tool_calls
estimated_llm_cost
estimated_tool_cost
total_estimated_cost
task_success
```

---

# 13. Economics by Use Case

Different use cases should have different acceptable cost profiles.

## Domain Expert

Higher cost may be acceptable when:

- complex reasoning is required;
- multiple scientific sources must be synthesized;
- answer quality materially improves.

## Analytics / Text2SQL

Cost should remain controlled because deterministic database execution performs the actual computation.

The LLM should mainly support:

- intent interpretation;
- query generation;
- explanation.

## Customer Support

Cost sensitivity is high because this workflow may have high interaction volume.

The preferred model profile should prioritize:

```text
low latency
+
low cost
+
reliable tool use
```

---

# 14. Business-Level Metrics

Technical AI cost can later be connected to business outcomes.

Possible metrics include:

```text
AI cost per support conversation

AI cost per qualified lead

AI cost per consultation request

AI cost per successful booking

AI cost per returning user

AI cost per resolved support task
```

This allows model economics to be evaluated in product terms rather than only infrastructure terms.

---

# 15. Initial Optimization Strategy

The target architecture follows these initial cost-control principles:

1. use a small or fast model for routing;
2. use stronger reasoning models only when justified;
3. use deterministic computation instead of LLM calculation;
4. avoid unnecessary model calls;
5. keep retrieval context relevant and compact;
6. reuse embeddings;
7. use tools for structured and live data;
8. evaluate cost together with task success;
9. compare providers using the same test cases;
10. optimize cost per successful task rather than only cost per token.

---

# 16. Current Status

The project currently has the architecture required to begin collecting economics data, but complete cost instrumentation has not yet been implemented.

Current work already provides useful building blocks:

```text
explicit routes
+
tool calls
+
execution traces
+
model calls
+
evaluation cases
```

The next stages will extend traces with:

```text
provider
model
token usage
latency
estimated cost
task success
```

Actual provider pricing and measured cost comparisons will be added after multi-model experiments are implemented.
