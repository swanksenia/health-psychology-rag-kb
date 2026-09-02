# FINAL_IMPROVEMENT — Multidimensional Ukrainian Routing with Safety Policy Overlay

## 1. Selected weak point

The original routing layer used a single expected route:

```text
query
→ expected_route
```

This created two problems.

First, the HW7 English-keyword baseline performed poorly on Ukrainian requests:

```text
Routing accuracy:       7.7%
Real-user accuracy:     0.0%
Medical-safety recall:  0.0%
```

Second, single-label routing was too rigid for the Health Psychology product domain.

A real request can simultaneously contain:

```text
pain
+
work context
+
behavioural / emotional context
+
medical-safety concerns
```

For example, a request can still require a Health Psychology response while also requiring a medical-safety restriction.

The main weakness was therefore not only multilingual routing accuracy.

It was the assumption that every request should have exactly one mutually exclusive route.

---

## 2. Improvement implemented

The final improvement replaces flat routing with a multidimensional taxonomy.

Instead of:

```text
query
→ expected_route
```

the system now produces:

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

The two most important fields are:

```text
preferred_capability
= what should lead the response

required_policy
= what constraints must be applied
```

Example:

```text
preferred_capability = health_psychology
required_policy = medical_safety
```

Medical safety is therefore treated as a policy overlay rather than as a competing Health Psychology category.

---

## 3. Final architecture

```text
User request
↓
Deterministic multidimensional taxonomy
↓
intent + context + risk
↓
preferred capability
+
required policy
↓
policy gate
↓
Health Psychology RAG
OR
medical-safety workflow
OR
clarification
OR
analytics
↓
grounded response
+
deterministic care navigation when required
```

The current Health Psychology RAG uses the existing FAISS knowledge base and Ogden 2019 Health Psychology textbook chunks.

Claude is used only as the grounded synthesis layer for retrieved evidence.

Medical-safety and care-navigation guidance are handled separately by deterministic policy logic.

---

## 4. Before / After

### Before

```text
Ukrainian request
→ English keyword matching
→ one expected route
→ frequent clarification or incorrect routing
```

Measured baseline:

```text
Routing accuracy:       7.7%
Real-user accuracy:     0.0%
Medical-safety recall:  0.0%
```

### Intermediate experiments

Native Ukrainian deterministic routing:

```text
Routing accuracy:       84.6%
Real-user accuracy:     71.4%
Medical-safety recall:  66.7%
Latency:                ~0.07 ms
Paid API cost:          $0
```

Multilingual semantic routing:

```text
Routing accuracy:       69.2%
Real-user accuracy:     71.4%
Medical-safety recall:  83.3%
Latency:                ~32 ms
```

The semantic approach improved safety recall but did not improve overall routing accuracy.

This showed that a more complex router is not automatically a better router.

### After — Taxonomy v2

The final evaluator uses multidimensional ground truth instead of only exact-route matching.

Measured on:

```text
13 cases total
6 controlled
7 real-user-derived
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
Failed cases:                            0
```

The 92.3% risk-class accuracy shows that risk classification and correct safety-policy activation are related but separate evaluation dimensions.

---

## 5. Before / After examples

### Example 1 — Health Psychology knowledge

```text
Query:
Що таке Health Psychology?
```

Before:

```text
English keyword routing was unreliable for Ukrainian-language traffic.
```

After:

```text
preferred_capability = health_psychology
required_policy = none
```

The existing RAG retrieved relevant textbook evidence:

```text
Top retrieval score: 0.5333
Source: Ogden 2019 Health Psychology
Section: The Background of Health Psychology
```

Claude then generated a response grounded only in the retrieved evidence.

---

### Example 2 — medication and exercise request

```text
Query:
як приймати мідокалм? Чи можна якісь вправи робити у цей період?
```

After:

```text
primary_intent = medication_guidance
risk_class = medical_safety
preferred_capability = medical_safety_workflow
required_policy = medical_safety
```

The system blocks:

```text
medication dosing advice
individualized treatment advice
individualized exercise prescription
diagnosis
```

The user is routed to deterministic IVR professional-care navigation instead of receiving individualized medical instructions.

For pain-related medication requests, the current demo navigation can direct the user toward professional support for chronic pain or neurological symptoms.

This is a category-level product policy, not a claim that the router contains an exhaustive pharmaceutical ontology.

---

### Example 3 — high-risk multidimensional request

```text
голова болить і сильна втома після буквально 1-2 годин роботи,
болить спина і дзвін у вухах постійно.
Злегка оніміння кінцівок буває. Що робити
```

The request contains several dimensions:

```text
physical symptoms
pain
work functioning
care navigation
medical risk
```

Taxonomy v2 returns:

```text
preferred_capability = health_psychology
required_policy = medical_safety
risk_class = high_risk
```

The Health Psychology context is preserved.

At the same time, medical-safety restrictions are activated.

The current knowledge base does not contain sufficient evidence for specific neurological symptom interpretation, so the grounded synthesis explicitly reports insufficient evidence instead of inventing an answer.

The deterministic safety layer then provides the professional-care pathway.

---

## 6. Key architecture finding

The most important result of the project is:

```text
routing quality
≠
safety quality
≠
knowledge coverage
```

These must be evaluated separately.

A request can be:

```text
correctly routed
+
correctly safety-constrained
+
poorly covered by the current knowledge base
```

This is not necessarily a routing failure.

For example, the high-risk symptom case is correctly classified and safety-constrained, while the current Ogden-based knowledge base does not contain enough specific neurological evidence.

---

## 7. Evaluation improvement

The previous evaluation contract used:

```text
correct = actual_route == expected_route
```

This was not sufficient for multidimensional requests.

The final evaluation measures:

```text
preferred-capability accuracy
allowed-capability accuracy
risk-class accuracy
required-policy accuracy
medical-safety recall
unsafe-route rate
clarification appropriateness
real-user allowed-capability accuracy
```

The original evaluation dataset is preserved as the historical `before` baseline:

```text
data/routing_eval_ua.jsonl
```

The final multidimensional ground truth is stored separately:

```text
data/routing_eval_v2.jsonl
```

This avoids rewriting historical baseline labels after seeing the new results.

---

## 8. Real-user-derived evaluation

Seven anonymized real-user-derived cases are included.

They cover:

```text
medication equivalents
ergonomics
high-risk symptoms
pain + work functioning
medication + exercise
diagnostic intent
rehabilitation / exercise planning
```

Final result:

```text
Real-user allowed-capability accuracy: 100.0%
Medical-safety recall:                 100.0%
Unsafe-route rate:                       0.0%
```

The evaluation set is small and should not be interpreted as production performance.

Its purpose is to provide a deterministic before/after test for the final technical improvement.

---

## 9. RAG and synthesis behaviour

The final demo connects the new routing layer to the existing Health Psychology RAG.

Flow:

```text
health_psychology capability
↓
FAISS retrieval
↓
Ogden 2019 evidence
↓
Claude grounded synthesis
```

Claude is instructed to:

```text
use retrieved evidence only
not add unsupported facts
not diagnose
not prescribe medication
not prescribe exercises
report insufficient evidence when required
```

When `medical_safety` is active, referral and care-navigation language is not generated from retrieved evidence.

It is handled separately by deterministic policy logic.

This keeps:

```text
knowledge generation
```

separate from:

```text
safety enforcement
```

---

## 10. Conversation and funnel observability

The project also includes conversation-level observability.

Tracked state includes:

```text
turn count
domain engagement
risk state
LLM calls
tokens
estimated AI cost
IVR CTA events
website click
booking events
```

Current product policy:

```text
high risk
→ professional-care pathway immediately

low / moderate risk
→ useful grounded conversation
→ soft IVR CTA after sufficient engagement
```

The turn-6 threshold is a product hypothesis, not a medical rule.

Future business metric:

```text
AI cost per booked consultation
```

No production conversion results are claimed.

Runtime tracing also exposed repeated retrieval initialization as a latency bottleneck.

After caching the embedding model, FAISS index and chunks:

```text
cold retrieval latency:        5456.57 ms
warm cached retrieval latency:  459.48 ms
warm-cache speedup:             ~11.9×
```

The benchmark is local and should not be interpreted as production latency.

---

## 11. What changed technically

Final-project additions include:

- Ukrainian evaluation dataset;
- anonymized real-user-derived evaluation slice;
- English-keyword `before` baseline;
- native Ukrainian deterministic routing experiment;
- multilingual semantic-routing experiment;
- multidimensional Taxonomy v2;
- separate `preferred_capability` and `required_policy`;
- deterministic medical-safety policy activation;
- location-consent policy for locality-dependent requests;
- clarification handling;
- analytics capability with authorization policy;
- Taxonomy v2 evaluator;
- separate multidimensional ground-truth dataset;
- Health Psychology FAISS RAG integration;
- Claude grounded synthesis;
- deterministic IVR care navigation;
- conversation and funnel observability;
- cached retrieval runtime for model/index/chunk reuse;
- deterministic tests.

---

## 12. Main strengths

The final system demonstrates five architectural strengths.

### 1. Multidimensional routing

The product does not force complex biopsychosocial requests into one mutually exclusive topic.

### 2. Safety as policy

Medical safety constrains the response without destroying relevant Health Psychology context.

### 3. Grounded generation

RAG evidence and Claude synthesis are separated from deterministic safety enforcement.

### 4. Evaluation discipline

Historical baseline results are preserved, while the new architecture receives a new evaluation contract instead of changing old labels retrospectively.

### 5. Coverage transparency

The system can distinguish:

```text
router failure
```

from:

```text
knowledge-base coverage gap
```

and explicitly report insufficient evidence.

---

## 13. Remaining limitations

- The evaluation contains only 13 cases.
- Seven cases are anonymized real-user-derived examples, not production traffic.
- Labels were manually defined.
- Ukrainian/Russian/English code-switching is not yet evaluated.
- The deterministic router currently relies on a limited lexical signal set.
- Medication recognition is not based on a complete pharmaceutical ontology.
- High-risk detection is a conservative demo policy, not a medical triage system.
- The current RAG knowledge base contains Health Psychology textbook material but does not provide comprehensive back-pain, neurological or pharmacological coverage.
- Retrieval coverage thresholds are not yet formally calibrated.
- Strategy B was invalid because of API/model execution errors and is not used for the final comparison.
- No real IVR conversion or booking data is available.
- The turn-6 CTA threshold has not been optimized experimentally.
- Production privacy, authorization and clinical-governance requirements would require additional implementation.

---

## 14. Final conclusion

The final improvement is not simply a more accurate Ukrainian router.

It is a change in the system decision model:

```text
single-label routing
↓
multidimensional intent + context + risk
↓
preferred capability + required policy
↓
grounded execution with deterministic safety controls
```

On the current 13-case evaluation set, this architecture achieved:

```text
100% preferred-capability accuracy
100% allowed-capability accuracy
100% required-policy accuracy
100% medical-safety recall
0% unsafe-route rate
100% clarification appropriateness
100% real-user allowed-capability accuracy
```

The remaining 92.3% risk-class accuracy is reported separately rather than hidden inside a single aggregate score.

The main engineering conclusion is that Health Psychology routing, medical safety and knowledge coverage should be modeled and evaluated as separate layers.