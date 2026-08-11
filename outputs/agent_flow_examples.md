# Agent Flow Examples

## Example 1 — Supported course-content question

**Question:**  
What is the biopsychosocial model of health?

**Route:**  
`course_content`

**Tools called:**  
- `retrieve_course_content`
- `gemini_generate_content`

**Retrieved chunks:**  
- `ogden_2019_health_psychology__0013`
- `wright_2019_3p_disease_model__0010`
- `wright_2019_3p_disease_model__0007`

**Observation:**  
The agent routed the question to the `course_content` workflow, retrieved relevant Health Psychology chunks, and generated a grounded answer with source references.

**Final answer:**  
Based on the provided course materials, the biopsychosocial model of health is defined as follows:

* **Core Definition:** It is a model that explains health and illness through the interaction of biological, psychological, and social factors (Source chunk ID: `ogden_2019_health_psychology__0013`). 
* **Origin and Role:** It was developed, in part, as a response to biological reductionism and plays an integral role across multiple disciplines, including health psychology and behavioral medicine (Source chunk ID: `wright_2019_3p_disease_model__0007`).
* **Characteristics and Limitations:** While the model states that multiple disciplines contribute to health and disease, it lacks a specific framework for understanding *how* these biological, psychological, and socio-environmental factors contribute at each stage of disease development, maintenance, or treatment (Source chunk ID: `wright_2019_3p_disease_model__0010`).

---

## Example 2 — Weak vs grounded prompt

**Question:**  
What is the biopsychosocial model of health?

### Weak prompt

Based on the provided context, the biopsychosocial model of health:

* **Explains health and illness** through the interaction of biological, psychological, and social (or socio-environmental) factors.
* **Was developed as a response**, in part, to biological reductionism.
* **States that multiple disciplines contribute to health and disease**, playing an integral role across various fields, including health psychology and behavioral medicine.
* **Lacks a framework** (as noted by some critics) for understanding *how* these biological, psychological, and socio-environmental factors contribute to each stage of disease development, maintenance, or treatment.

### Grounded prompt

Based on the provided course materials, the biopsychosocial model is a model that:

* Explains health and illness through the interaction of biological, psychological, and social (or socio-environmental) factors (Source: ogden_2019_health_psychology__0013, wright_2019_3p_disease_model__0010).
* States that multiple disciplines contribute to health and disease (Source: wright_2019_3p_disease_model__0010).
* Was developed, in part, as a response to biological reductionism and plays an integral role in health psychology and behavioral medicine (Source: wright_2019_3p_disease_model__0007).

**Observation:**  
Both prompts produced a relevant answer because the retrieved context was sufficient. However, the grounded prompt explicitly cited the source chunk IDs, while the weak prompt did not. This demonstrates that explicit citation instructions improve traceability.

---

## Example 3 — Fallback behavior

**Question:**  
In health psychology, what are the DSM-5 diagnostic criteria for schizophrenia?

**Route:**  
`course_content`

**Retrieved chunks:**  
- `wright_2019_3p_disease_model__0008`
- `ogden_2019_health_psychology__0005`
- `wright_2019_3p_disease_model__0007`

### Weak prompt

Based on the provided context, there is no mention of the DSM-5 diagnostic criteria for schizophrenia.

### Grounded prompt with fallback

I do not have enough information in the provided course materials.

**Observation:**  
The retrieved context did not contain the requested DSM-5 diagnostic criteria. The weak prompt avoided inventing an answer in this run, while the grounded prompt followed the explicit fallback rule and returned the predefined missing-information response.

---

## Example 4 — Course structure route

**Question:**  
What topics are covered in the Health Psychology course?

**Route:**  
`course_structure`

**Tools called:**  
- `retrieve_course_structure`
- `gemini_generate_content`

**Retrieved chunks:**  
- `health_psychology_course_syllabus__0000`
- `health_psychology_course_syllabus__0006`
- `health_psychology_course_syllabus__0003`

**Observation:**  
The router selected the `course_structure` workflow. The retrieval tool returned syllabus-only chunks, demonstrating a separate retrieval strategy for course navigation.

**Final answer:**  
Based on the provided course materials, the course covers:

* The dynamic interaction between biological, social, and psychological factors that influence physical health and illness, with the goal of promoting overall well-being and preventing diseases (Source: `health_psychology_course_syllabus__0000`).
* Theoretical frameworks and concepts that form the foundation of a psychological perspective on physical health (Source: `health_psychology_course_syllabus__0003`).

---

## Example 5 — Clarification route

**Question:**  
Tell me something interesting.

**Route:**  
`clarification`

**Tools called:**  
None

**Observation:**  
The question could not be mapped to the supported Health Psychology workflows.

**Final answer:**  
Could you clarify your question? I can help with Health Psychology course content or course structure.


---

# State After Step Summaries

## Example 1 — Supported course-content question

```json
{
  "user_goal": "What is the biopsychosocial model of health?",
  "selected_route": "course_content",
  "tool_calls": [
    "retrieve_course_content",
    "gemini_generate_content"
  ],
  "final_answer_status": "generated"
}
```

## Example 2 — Weak vs grounded prompt

```json
{
  "user_goal": "What is the biopsychosocial model of health?",
  "selected_route": "course_content",
  "tool_calls": [
    "retrieve_course_content",
    "gemini_generate_content"
  ],
  "final_answer_status": "generated"
}
```

## Example 3 — Fallback behavior

```json
{
  "user_goal": "In health psychology, what are the DSM-5 diagnostic criteria for schizophrenia?",
  "selected_route": "course_content",
  "tool_calls": [
    "retrieve_course_content",
    "gemini_generate_content"
  ],
  "final_answer_status": "generated"
}
```

## Example 4 — Course structure route

```json
{
  "user_goal": "What topics are covered in the Health Psychology course?",
  "selected_route": "course_structure",
  "tool_calls": [
    "retrieve_course_structure",
    "gemini_generate_content"
  ],
  "final_answer_status": "generated"
}
```

## Example 5 — Clarification route

```json
{
  "user_goal": "Tell me something interesting.",
  "selected_route": "clarification",
  "tool_calls": [],
  "final_answer_status": "generated"
}
```
