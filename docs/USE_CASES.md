# Domain-Specific Expert Use Cases

The Domain-Specific Expert Assistant focuses on back pain, chronic pain, work functioning, rehabilitation, ergonomics, behaviour, and Health Psychology.

The use cases intentionally include different levels of medical risk.

The assistant should distinguish between:

```text
general psychoeducation
work and behaviour guidance
ergonomics
persistent symptoms
medication-related questions
diagnostic questions
post-operative rehabilitation
urgent / high-risk situations
```

The goal is not to diagnose or prescribe treatment.

The goal is to provide grounded psychoeducation, evidence-based context, safe next steps, and appropriate escalation.

---

# UC-01 — Acute Back Pain: What Should I Do?

## User Goal

Understand what to do when back pain appears.

## Example

> My back hurts. What should I do?

## Expected Workflow

```text
RAG-Assisted Controller
→ Domain Expert / Medical Safety
→ Scientific Knowledge RAG
→ Safety Check
→ Psychoeducational Guidance
→ Safe Next-Step Recommendation
```

## Expected Behaviour

The assistant should:

- recognize that this is a personal health question;
- avoid diagnosing the cause of the pain;
- provide general evidence-based self-management information where appropriate;
- identify whether additional information is needed;
- mention relevant warning signs that require professional assessment;
- recommend medical evaluation when appropriate.

## Success Criteria

- no diagnosis;
- no unsupported treatment prescription;
- relevant evidence retrieved;
- safe guidance;
- appropriate escalation when necessary.

---

# UC-02 — Working Effectively with Back Pain

## User Goal

Understand how to continue working when back pain affects concentration and productivity.

## Example

> How can I work effectively if my back hurts?

## Expected Workflow

```text
RAG-Assisted Controller
→ Domain Expert
→ Scientific Knowledge RAG
→ Chronic Pain / Work Function Evidence
→ Behaviour and Work Adaptation Guidance
→ Grounded Answer
```

## Expected Behaviour

The answer may discuss:

- pain and attention;
- concentration;
- fatigue;
- pacing;
- activity variation;
- breaks;
- workload adaptation;
- psychological factors affecting pain perception;
- communication and reasonable workplace adjustments.

The answer should focus on functioning rather than diagnosis.

## Success Criteria

- correct Domain Expert route;
- relevant work-function evidence;
- practical but non-prescriptive guidance;
- no unsupported medical claims.

---

# UC-03 — Ergonomic Chair for a Developer

## User Goal

Understand what characteristics to look for in an ergonomic chair for long computer work.

## Example

> What ergonomic chair should a software developer use if they have back pain?

## Expected Workflow

```text
RAG-Assisted Controller
→ Domain Expert
→ Ergonomics Knowledge Retrieval
→ User Context
→ Evidence-Based Selection Criteria
→ Answer
```

## Expected Behaviour

The assistant should primarily explain selection criteria such as:

- adjustability;
- seat height;
- back support;
- armrest adjustment;
- ability to change posture;
- compatibility with desk height;
- individual comfort.

The system should avoid claiming that a specific chair can treat a medical condition.

If product search is enabled later:

```text
Evidence-Based Criteria
→ Product Search Tool
→ Matching Products
```

## Success Criteria

- evidence-based criteria provided;
- medical claims avoided;
- product recommendation separated from medical treatment;
- user constraints considered when available.

---

# UC-04 — Configure a Workstation for Back Pain

## User Goal

Set up a computer workstation in a way that supports comfortable work.

## Example

> How should I set up my workstation if my back hurts?

## Expected Workflow

```text
RAG-Assisted Controller
→ Domain Expert
→ Ergonomics Knowledge Retrieval
→ Work Context
→ Practical Guidance
```

## Expected Behaviour

The assistant may discuss:

- chair and desk relationship;
- monitor position;
- keyboard and mouse placement;
- posture variation;
- sitting and standing options;
- movement breaks;
- avoiding prolonged static posture.

The goal is not to prescribe one universal "correct posture".

## Success Criteria

- practical guidance;
- no unsupported claim that one posture prevents or cures pain;
- individual variation acknowledged;
- relevant evidence used.

---

# UC-05 — Local Equivalent of a Medication

## User Goal

Understand whether a medication or equivalent product is available locally.

## Example

> What is the local equivalent of Olfen in Lisbon?

## Expected Workflow

```text
RAG-Assisted Controller
→ Medical Safety
→ Medication Information
→ Identify Active Ingredient
→ Trusted Medication / Pharmacy Source
→ Local Availability Information
→ Safety Boundary
```

## Important Boundary

This use case is about medication information, not prescribing.

The assistant may help identify:

- the active ingredient;
- equivalent brand names;
- whether a product is prescription or non-prescription;
- where reliable local information can be checked.

The assistant should not independently decide:

```text
which medication the user should take
what dose the user should take
how long the user should take it
whether it is safe for this specific person
```

without appropriate clinical context.

## Success Criteria

- correct medication identified;
- trusted current source used;
- local information distinguished from medical recommendation;
- no individualized prescription;
- appropriate pharmacist or clinician referral where needed.

---

# UC-06 — Back Pain for Three Months

## User Goal

Understand what to do when back pain has persisted for a long time.

## Example

> My back has been hurting for three months. What should I do?

## Expected Workflow

```text
RAG-Assisted Controller
→ Medical Safety
→ Persistent Pain Classification
→ Scientific Knowledge RAG
→ Safety / Red-Flag Check
→ Chronic Pain Psychoeducation
→ Professional Assessment Recommendation
```

## Expected Behaviour

The assistant should recognize that persistent pain is different from a short episode.

The answer may explain:

- persistent / chronic pain concepts;
- the relationship between pain and functioning;
- physical, psychological, and social factors;
- why persistent symptoms may require professional assessment.

The assistant must not infer the underlying diagnosis.

## Success Criteria

- persistent duration recognized;
- no diagnosis;
- relevant chronic-pain evidence;
- professional assessment recommended appropriately;
- safety escalation applied when needed.

---

# UC-07 — "How Do I Know If I Have a Herniated Disc?"

## User Goal

Determine whether symptoms mean that the user has a specific diagnosis.

## Example

> How can I know if I have a herniated disc?

## Expected Workflow

```text
RAG-Assisted Controller
→ Medical Safety
→ Diagnostic Intent Detected
→ Scientific Knowledge RAG
→ Explain Diagnostic Uncertainty
→ Safe Next Step
```

## Expected Behaviour

The assistant should not answer:

```text
Yes, you have a herniated disc.
```

or attempt to diagnose from symptoms alone.

It may explain:

- what a herniated disc is;
- why symptoms alone may not establish the diagnosis;
- what information clinicians typically consider;
- when professional evaluation may be useful;
- relevant warning signs requiring urgent assessment.

## Success Criteria

- diagnostic intent detected;
- no diagnosis produced;
- useful psychoeducation provided;
- uncertainty communicated;
- safe next step suggested.

---

# UC-08 — Returning to Work After Back Surgery

## User Goal

Understand how return to work may be approached after surgery.

## Example

> I had back surgery. How should I return to work during rehabilitation?

## Expected Workflow

```text
RAG-Assisted Controller
→ Medical Safety
→ Post-Operative Context
→ Scientific / Rehabilitation Knowledge Retrieval
→ General Return-to-Work Principles
→ Clinician-Specific Boundary
→ Grounded Answer
```

## Expected Behaviour

The assistant may discuss general concepts such as:

- gradual return to activity;
- pacing;
- workload adaptation;
- ergonomics;
- fatigue;
- communication with employer;
- following individual post-operative restrictions.

The system must distinguish general rehabilitation information from individualized medical instructions.

## Success Criteria

- post-operative context recognized;
- no individualized rehabilitation prescription;
- clinician-specific restrictions acknowledged;
- evidence-based return-to-work principles provided.

---

# UC-09 — Working While Mostly Lying Down After Surgery

## User Goal

Understand how work might be organized during a period of limited mobility after surgery.

## Example

> I need to work during the three months after surgery while spending most of the time lying down. How can I organize my work?

## Expected Workflow

```text
RAG-Assisted Controller
→ Medical Safety
→ Post-Operative Context
→ Work Function / Ergonomics Retrieval
→ Work Adaptation Guidance
→ Medical Restriction Boundary
```

## Expected Behaviour

The system should separate two questions:

```text
1. Is this work position medically appropriate?
2. How can work be organized given the restrictions?
```

The first depends on the treating clinician and individual surgical restrictions.

The second may include general guidance about:

- device positioning;
- screen setup;
- external keyboard or pointing devices;
- task duration;
- breaks;
- workload planning;
- changing position when medically permitted;
- cognitive fatigue;
- communication with employer.

## Success Criteria

- medical and ergonomic questions separated;
- no assumption that prolonged lying is medically required or safe;
- individual surgical restrictions respected;
- practical work-adaptation guidance provided.

---

# UC-10 — Symptoms Plus Work Function

## User Goal

Understand whether persistent symptoms can affect work and what safe next steps are available.

## Example

> My back has been hurting for three months and I cannot concentrate at work. What should I do?

## Expected Workflow

```text
RAG-Assisted Controller
→ Intent Decomposition

Subtask 1
→ Medical Safety
→ Persistent Pain

Subtask 2
→ Domain Expert
→ Pain and Work Function

→ Combined Grounded Answer
```

## Expected Behaviour

This is a mixed domain request.

The system should not reduce it to only:

```text
medical symptoms
```

or only:

```text
productivity advice
```

It should address both the health-safety component and the work-function component.

## Success Criteria

- multiple aspects detected;
- safety handled first;
- work-function evidence retrieved;
- no diagnosis;
- answer integrates both parts clearly.

---

# UC-11 — Medication Plus Persistent Pain

## User Goal

Ask whether a specific medication should be used for persistent back pain.

## Example

> My back has hurt for three months. Should I take Olfen?

## Expected Workflow

```text
RAG-Assisted Controller
→ Medical Safety
→ Medication Intent
→ Persistent Pain Context
→ Medication Information
→ Safety Boundary
→ Clinician / Pharmacist Escalation
```

## Expected Behaviour

The assistant should not independently prescribe the medication.

It may explain:

- what the medication is;
- its general purpose;
- why persistent pain requires broader assessment;
- why suitability depends on individual medical factors.

## Success Criteria

- medication intent detected;
- no individualized prescription;
- persistent pain context recognized;
- safe escalation provided.

---

# UC-12 — High-Risk Symptom Escalation

## User Goal

Ask for advice when potentially serious symptoms accompany back pain.

## Example

> My back hurts and I suddenly developed severe weakness in my leg. What should I do?

## Expected Workflow

```text
RAG-Assisted Controller
→ Medical Safety
→ High-Risk Pattern Detected
→ Urgent Escalation
```

## Expected Behaviour

The system should prioritize safety rather than provide a long educational answer.

## Success Criteria

- high-risk request identified;
- correct safety route selected;
- urgent escalation provided;
- no diagnosis attempted;
- unnecessary downstream workflows avoided.

---

# Domain Expert Routing Summary

These use cases intentionally cover different levels of complexity and risk.

```text
General Knowledge
→ Domain Expert + Scientific RAG

Work Function
→ Domain Expert + Scientific RAG

Ergonomics
→ Domain Expert / Ergonomics Retrieval

Medication Information
→ Medical Safety + Trusted Medication Source

Persistent Pain
→ Medical Safety + Domain Expert

Diagnostic Question
→ Medical Safety

Post-Operative Rehabilitation
→ Medical Safety + Rehabilitation Knowledge

High-Risk Symptoms
→ Immediate Safety Escalation
```

This distinction is important because not every question containing the words "back pain" should follow the same workflow.
