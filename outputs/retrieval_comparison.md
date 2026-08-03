# Retrieval Comparison

## Evaluation Summary

- Baseline Top-1 accuracy: 83.3%
- Improved Top-1 accuracy: 100.0%
- Baseline Recall@3: 100.0%
- Improved Recall@3: 100.0%
- Queries improved: 1
- Queries degraded: 0

## Query-Level Comparison

| Query | Baseline top-1 | Improved top-1 | What changed |
|---|---|---|---|
| What is the biopsychosocial model of health? | `ogden_2019_health_psychology__0013` | `ogden_2019_health_psychology__0013` | No change: the correct top result was preserved. |
| What are the components of the COM-B model? | `michie_2011_behaviour_change_wheel__0032` | `michie_2011_behaviour_change_wheel__0032` | No change: the correct top result was preserved. |
| How does the Behaviour Change Wheel support intervention design? | `michie_2011_behaviour_change_wheel__0059` | `michie_2011_behaviour_change_wheel__0059` | No change: the correct top result was preserved. |
| What are the predisposing, precipitating, and perpetuating factors in the 3P model? | `wright_2019_3p_disease_model__0016` | `wright_2019_3p_disease_model__0113` | The expected document remained correct, but hybrid scoring changed the top chunk. |
| How can stress affect physical health? | `ogden_2019_health_psychology__0135` | `ogden_2019_health_psychology__0135` | No change: the correct top result was preserved. |
| What topics are covered in the Health Psychology course? | `ogden_2019_health_psychology__0245` | `health_psychology_course_syllabus__0000` | Improved: the expected document moved to rank one after metadata filtering. |

## Analysis

Metadata filtering produced the largest positive effect. For the course-topics query, it removed textbook chunks and moved the syllabus from rank two to rank one.

Hybrid scoring changed the chunk ranking for the 3P-model query. The promoted chunk had stronger keyword overlap, but it was not necessarily a more direct answer than the baseline top chunk.

## Conclusion

The improved pipeline increased document-level Top-1 accuracy from 83.3% to 100%. Metadata filtering was the most effective improvement, while simple hybrid reranking had a mixed effect on chunk-level relevance.