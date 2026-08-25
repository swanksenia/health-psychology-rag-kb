# Homework 7 — Workflow Examples

The following examples were produced by the compiled LangGraph workflow.

## Scenario 1 — Health Psychology question

**Request:** Why can't I work effectively with chronic back pain?

**Trusted role:** `user`

**Selected route:** `health_psychology`

**Analytics access:** `None`

**Execution path:**

```text
classify_request -> retrieve_health_psychology -> build_answer
```

**Final answer:**

Relevant Health Psychology context was retrieved about chronic pain, pain perception, psychological factors, and daily functioning.

---

## Scenario 2 — Analytics request — admin

**Request:** Show me product analytics for the last 7 days.

**Trusted role:** `admin`

**Selected route:** `analytics`

**Analytics access:** `True`

**Execution path:**

```text
classify_request -> check_analytics_access -> get_usage_analytics -> build_answer
```

**Final answer:**

Product analytics for the last 7 days: 6 users, 9 sessions, and 15 queries.

---

## Scenario 3 — Analytics request — external user

**Request:** Show me product analytics for the last 7 days.

**Trusted role:** `user`

**Selected route:** `analytics`

**Analytics access:** `False`

**Execution path:**

```text
classify_request -> check_analytics_access -> deny_access -> build_answer
```

**Final answer:**

Access denied. Product analytics are available only to authorized internal users.

---

## Scenario 4 — Unclear request

**Request:** I feel tired and annoyed lately and I don't know why.

**Trusted role:** `user`

**Selected route:** `clarification`

**Analytics access:** `None`

**Execution path:**

```text
classify_request -> ask_clarification -> build_answer
```

**Final answer:**

Please clarify whether your question is about Health Psychology content or product analytics.

---
