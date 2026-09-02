# Короткий сценарій захисту

## 1. Контекст — 20–30 секунд

Мій проєкт — domain-specific expert assistant для Health Psychology та chronic/back pain, орієнтований на IVR.

За курс я поступово побудувала knowledge base, retrieval, RAG, tool layer, medical-safety workflow, LangGraph orchestration та evaluation/observability.

У фінальному проєкті я не хотіла додавати ще одну технологію. Я подивилась на систему як продакт: якщо routing для українського користувача неточний або занадто дорогий, ця архітектура не має бізнес-сенсу.

## 2. Weak point

Поточний HW7 baseline використовує English keyword routing.

На українських запитах це крихко: навіть зрозумілий запит часто падає у clarification.

Моя гіпотеза:

> більш складний router може підвищити accuracy, але він не повинен коштувати дорожче без достатнього приросту якості.

Тому я порівнюю не тільки accuracy, а **cost per correct routing decision**.

## 3. Що я реалізувала

Три стратегії:

```text
A — native Ukrainian deterministic rules
B — translate Ukrainian to English, then route
C — multilingual semantic embeddings
```

Перед усіма трьома є спільний deterministic medical-safety pre-gate.

Тобто очевидний medication / diagnostic / treatment request не потребує дорогого semantic decision, щоб потрапити в safety workflow.

## 4. Offline before/after

На поточному невеликому наборі:

```text
HW7-style English baseline:
1 / 13 correct
7.7%

Native Ukrainian rules:
11 / 13 correct
84.6%
```

Це ще не фінальний winner, тому що B/C треба прогнати в Colab на тому самому set.

Два складних кейси, які native rules ще не закривають:
- довгий natural-language pain narrative;
- складна rehabilitation/exercise strategy.

Саме на таких кейсах semantic routing може виправдати свою додаткову cost.

## 5. Real-user-derived examples

Наприклад:

```text
"місцеві аналоги Олфену"
```

це medication intent → medical-safety route.

Якщо локальність справді потрібна, бот не мовчки читає location:
- просить permission;
- отримує approximate location від browser;
- визначає city;
- перепитує: "Схоже, ви зараз у <city>. Правильно?";
- зберігає тільки підтверджене місто.

Інший кейс:

```text
"Ергономічний стул"
```

Я не хочу відповідати маркетинговим припущенням "ергономічний стілець вирішує біль".

Я додала evidence registry: chair-specific evidence обмежене/суперечливе, а sitting behavior, статичність та перерви мають окрему evidence base.

## 6. Conversation funnel

Я також додала observability, щоб потім оцінювати не лише routing:

```text
conversation
→ IVR CTA
→ clinic discussion
→ website
→ booking
```

Трекуються turn count, domain depth, tokens і cost.

Для low/moderate risk soft CTA стає eligible після 6-го turn.

Для high-risk safety case — не чекаємо 6 turns, professional-care pathway запускається одразу.

## 7. Business metric

Фінально мене цікавить не просто дешевий inference.

Мета:

> мінімальна AI cost при acceptable routing + safety quality.

У production наступна метрика:

```text
AI cost per booked IVR consultation
```

і вже її треба порівнювати з CAC інших каналів.

Але я не вигадую цю цифру зараз — production conversion data у мене немає.

## 8. Limitations

- eval set малий;
- semantic threshold ще не calibrated;
- code-switching не протестований;
- local embeddings мають infrastructure cost;
- booking funnel поки instrumented, а не інтегрований з production CRM;
- turn 6 — product hypothesis, яку треба A/B test;
- safety signals — conservative routing guardrail, не medical triage.
