# Agent Flow Examples

These examples show the execution trace of the Health Psychology & Chronic Back Pain Assistant.


## Example 1

### Question

How to change harmful behavior?

### Route

`psychoeducation`

### Tool called

- search_knowledge_base: {'query': 'How to change harmful behavior?'}

### Observation

- search_knowledge_base: success=True, result_count=3, chunks=['michie_2011_behaviour_change_wheel__0021', 'ogden_2019_health_psychology__0068', 'michie_2011_behaviour_change_wheel__0033']

### State after workflow

- user_goal: understand a health psychology topic using scientific evidence
- selected_route: psychoeducation
- plan: ['search_knowledge_base', 'build_final_answer']
- completed_steps: ['classify_request', 'build_plan', 'search_knowledge_base', 'build_final_answer']
- health_psychology_topics: ['behavior', 'harmful behavior']
- physical_back_pain_request: False
- spine_condition_detected: False
- medical_advice_requested: False
- care_pathway_needed: False
- fallback_used: True

### Final answer

LLM synthesis is temporarily unavailable because the API quota was exceeded. Relevant evidence was successfully retrieved from the knowledge base.


## Example 2

### Question

Why can't I work effectively with chronic pain?

### Route

`psychoeducation`

### Tool called

- search_knowledge_base: {'query': "Why can't I work effectively with chronic pain?"}

### Observation

- search_knowledge_base: success=True, result_count=3, chunks=['wright_2019_3p_disease_model__0033', 'wright_2019_3p_disease_model__0046', 'wright_2019_3p_disease_model__0037']

### State after workflow

- user_goal: understand a health psychology topic using scientific evidence
- selected_route: psychoeducation
- plan: ['search_knowledge_base', 'build_final_answer']
- completed_steps: ['classify_request', 'build_plan', 'search_knowledge_base', 'build_final_answer']
- health_psychology_topics: ['pain']
- physical_back_pain_request: False
- spine_condition_detected: False
- medical_advice_requested: False
- care_pathway_needed: False
- fallback_used: True

### Final answer

LLM synthesis is temporarily unavailable because the API quota was exceeded. Relevant evidence was successfully retrieved from the knowledge base.


## Example 3

### Question

My back hurts, and when I go to the gym to strengthen my back, the pain gets even worse. What should I do?

### Route

`back_pain_medical_request`

### Tool called

- search_knowledge_base: {'query': 'My back hurts, and when I go to the gym to strengthen my back, the pain gets even worse. What should I do? psychological behavioral aspects of pain pain perception health psychology'}
- get_ivr_care_options: {}

### Observation

- search_knowledge_base: success=True, result_count=3, chunks=['ogden_2019_health_psychology__0164', 'ogden_2019_health_psychology__0163', 'ogden_2019_health_psychology__0165']
- apply_medical_boundary: {'diagnosis_allowed': False, 'treatment_recommendations_allowed': False, 'medical_referral_required': True, 'psychoeducation_allowed': True}
- get_ivr_care_options: success=True, provider=Institute of Vertebrology and Rehabilitation, cities=['Kyiv', 'Lviv', 'Ivano-Frankivsk'], online_consultation=True

### State after workflow

- user_goal: understand a physical back-pain problem and what to do next
- selected_route: back_pain_medical_request
- plan: ['search_knowledge_base', 'apply_medical_boundary', 'get_ivr_care_options', 'add_biopsychosocial_context', 'build_final_answer']
- completed_steps: ['classify_request', 'build_plan', 'search_knowledge_base', 'apply_medical_boundary', 'get_ivr_care_options', 'add_biopsychosocial_context', 'build_final_answer']
- health_psychology_topics: ['pain']
- physical_back_pain_request: True
- spine_condition_detected: False
- medical_advice_requested: True
- care_pathway_needed: True
- fallback_used: True

### Final answer

I cannot diagnose the cause of your back pain or recommend medication or treatment based on this message. It would be appropriate to discuss your symptoms with a healthcare professional.

You can consult specialists at the Institute of Vertebrology and Rehabilitation. IVR provides care in Kyiv, Lviv, Ivano-Frankivsk, and online consultations are also available. https://ivr.ua/

LLM synthesis is temporarily unavailable because the API quota was exceeded. Relevant evidence was successfully retrieved from the knowledge base.


## Example 4

### Question

I have terrible lower back pain. Which painkillers should I use?

### Route

`back_pain_medical_request`

### Tool called

- search_knowledge_base: {'query': 'I have terrible lower back pain. Which painkillers should I use? psychological behavioral aspects of pain pain perception health psychology'}
- get_ivr_care_options: {}

### Observation

- search_knowledge_base: success=True, result_count=3, chunks=['ogden_2019_health_psychology__0151', 'ogden_2019_health_psychology__0165', 'ogden_2019_health_psychology__0166']
- apply_medical_boundary: {'diagnosis_allowed': False, 'treatment_recommendations_allowed': False, 'medical_referral_required': True, 'psychoeducation_allowed': True}
- get_ivr_care_options: success=True, provider=Institute of Vertebrology and Rehabilitation, cities=['Kyiv', 'Lviv', 'Ivano-Frankivsk'], online_consultation=True

### State after workflow

- user_goal: understand a physical back-pain problem and what to do next
- selected_route: back_pain_medical_request
- plan: ['search_knowledge_base', 'apply_medical_boundary', 'get_ivr_care_options', 'add_biopsychosocial_context', 'build_final_answer']
- completed_steps: ['classify_request', 'build_plan', 'search_knowledge_base', 'apply_medical_boundary', 'get_ivr_care_options', 'add_biopsychosocial_context', 'build_final_answer']
- health_psychology_topics: ['pain']
- physical_back_pain_request: True
- spine_condition_detected: False
- medical_advice_requested: True
- care_pathway_needed: True
- fallback_used: True

### Final answer

I cannot diagnose the cause of your back pain or recommend medication or treatment based on this message. It would be appropriate to discuss your symptoms with a healthcare professional.

You can consult specialists at the Institute of Vertebrology and Rehabilitation. IVR provides care in Kyiv, Lviv, Ivano-Frankivsk, and online consultations are also available. https://ivr.ua/

LLM synthesis is temporarily unavailable because the API quota was exceeded. Relevant evidence was successfully retrieved from the knowledge base.


## Example 5

### Question

I feel tired and annoyed lately and I don't know why.

### Route

`clarification`

### Tool called

None

### Observation

None

### State after workflow

- user_goal: clarify the user's request
- selected_route: clarification
- plan: ['build_clarification_answer']
- completed_steps: ['classify_request', 'build_plan', 'build_clarification_answer']
- health_psychology_topics: []
- physical_back_pain_request: False
- spine_condition_detected: False
- medical_advice_requested: False
- care_pathway_needed: False
- fallback_used: False

### Final answer

Could you clarify what you would like to understand? You can ask about health psychology, chronic pain, emotional responses to illness, or a back-pain concern.
