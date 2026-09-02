# Як додати Final Project у поточний GitHub repo

Рекомендований варіант — не розкидати фінальні файли по HW1–HW8.

Створи у корені repo:

```text
Final_Project/
```

і скопіюй туди весь вміст цього пакета.

Очікувана структура:

```text
health-psychology-rag-kb/
├── HW7_langgraph_orchestration/
├── HW8_evaluation_observability/
├── data/
├── index/
├── scripts/
├── ...
└── Final_Project/
    ├── README.md
    ├── FINAL_IMPROVEMENT.md
    ├── ARCHITECTURE_CARD.md
    ├── DEFENSE_SCRIPT_UA.md
    ├── Final_Project.ipynb
    ├── requirements.txt
    ├── config/
    ├── data/
    ├── outputs/
    ├── scripts/
    ├── tests/
    └── web/
```

## Fast check

From the `Final_Project` directory:

```bash
python scripts/evaluate_offline.py
pytest -q
python -m py_compile   scripts/multilingual_router.py   scripts/conversation_funnel.py   scripts/evaluate_offline.py
```

## Full benchmark

In Colab:

```bash
python scripts/multilingual_router.py
```

Then copy the actual A/B/C measurements from:

```text
outputs/routing_summary.json
```

into `FINAL_IMPROVEMENT.md`.

Do not invent missing B/C numbers.

## Commit

Example:

```bash
git add Final_Project
git commit -m "Add final cost-aware Ukrainian routing project"
git push
```
