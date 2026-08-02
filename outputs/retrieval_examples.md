# Semantic Retrieval Examples

**Embedding model:** `sentence-transformers/all-MiniLM-L6-v2`

**Vector index:** `FAISS IndexFlatIP`

**Top-k:** `3`

## Query 1

**Query:** What is the biopsychosocial model of health?

### Top-1

- **Chunk ID:** `ogden_2019_health_psychology__0013`
- **Score:** `0.7959`
- **Document ID:** `ogden_2019_health_psychology`
- **Source:** `data/raw/ogden_2019_health_psychology.pdf`
- **Section:** `1.The Biopsychosocial Model`
- **Text preview:** smoking), pressures to change behavior (e.g. peer group expectations, parental pressure), social values on health (e.g. whether health was regarded as a good or a bad thing), social class, the environment, and ethnicity. #### Fig 1 The biopsychosocial model of health and illness (after Engel 1977, 1980) ![Fig 1 The biopsychosocial model of health a

### Top-2

- **Chunk ID:** `wright_2019_3p_disease_model__0010`
- **Score:** `0.7779`
- **Document ID:** `wright_2019_3p_disease_model`
- **Source:** `data/raw/wright_2019_3p_disease_model.html`
- **Section:** `Introduction`
- **Text preview:** and disease are conceptualized or managed today ([Kontos, 2011](https://pmc.ncbi.nlm.nih.gov/articles/PMC6879427/#B55)). This could be, in part, because the biopsychosocial model lacks a framework for understanding *how* biological, psychological, and socio-environmental factors may contribute at each stage of disease development, in maintaining di

### Top-3

- **Chunk ID:** `wright_2019_3p_disease_model__0007`
- **Score:** `0.7735`
- **Document ID:** `wright_2019_3p_disease_model`
- **Source:** `data/raw/wright_2019_3p_disease_model.html`
- **Section:** `Introduction`
- **Text preview:** factors in health and disease ([Engel, 1977](https://pmc.ncbi.nlm.nih.gov/articles/PMC6879427/#B28); [Borrell-Carrió et al., 2004](https://pmc.ncbi.nlm.nih.gov/articles/PMC6879427/#B11)). The biopsychosocial model was developed as a response, in part, to biological reductionism ([Engel, 1977](https://pmc.ncbi.nlm.nih.gov/articles/PMC6879427/#B28))

**Comment:** Relevant. All three retrieved chunks discuss the biopsychosocial model. Top-1 provides the most direct explanation, while Top-2 and Top-3 add context about its structure, development, and limitations.

---

## Query 2

**Query:** What are the components of the COM-B model?

### Top-1

- **Chunk ID:** `michie_2011_behaviour_change_wheel__0032`
- **Score:** `0.4078`
- **Document ID:** `michie_2011_behaviour_change_wheel`
- **Source:** `data/raw/michie_2011_behaviour_change_wheel.html`
- **Section:** `Establishing criteria of usefulness`
- **Text preview:** [1](https://pmc.ncbi.nlm.nih.gov/articles/PMC3096582/#F1) represent potential influence between components in the system. For example, opportunity can influence motivation as can capability; enacting a behaviour can alter capability, motivation, and opportunity. #### Figure 1 ![The COM-B system - a framework for understanding behaviour](assets/mich

### Top-2

- **Chunk ID:** `michie_2011_behaviour_change_wheel__0040`
- **Score:** `0.3626`
- **Document ID:** `michie_2011_behaviour_change_wheel`
- **Source:** `data/raw/michie_2011_behaviour_change_wheel.html`
- **Section:** `Develop a new framework`
- **Text preview:** The new framework was developed by tabulating the full set of intervention categories that had been identified and establishing links between intervention characteristics and components of the COM-B system that may need to be changed. The definitions and conceptualisation of the intervention categories were refined through discussion and by consult

### Top-3

- **Chunk ID:** `michie_2011_behaviour_change_wheel__0060`
- **Score:** `0.3397`
- **Document ID:** `michie_2011_behaviour_change_wheel`
- **Source:** `data/raw/michie_2011_behaviour_change_wheel.html`
- **Section:** `Development of a new framework`
- **Text preview:** [2](https://pmc.ncbi.nlm.nih.gov/articles/PMC3096582/#T2) and [3](https://pmc.ncbi.nlm.nih.gov/articles/PMC3096582/#T3)). #### Table 2. Links between the components of the 'COM-B' model of behaviour and the intervention functions | Model of behaviour: sources | Education | Persuasion | Incentivisation | Coercion | Training | Restriction | Environme

**Comment:** Partially relevant. All retrieved chunks are related to COM-B, but the previews do not provide a single clear enumeration of capability, opportunity, motivation, and behaviour.

---

## Query 3

**Query:** How does the Behaviour Change Wheel support intervention design?

### Top-1

- **Chunk ID:** `michie_2011_behaviour_change_wheel__0059`
- **Score:** `0.6578`
- **Document ID:** `michie_2011_behaviour_change_wheel`
- **Source:** `data/raw/michie_2011_behaviour_change_wheel.html`
- **Section:** `Development of a new framework`
- **Text preview:** Figure 2 ![The Behaviour Change Wheel](assets/michie_2011_figure_2.jpeg) **Figure caption:** The Behaviour Change Wheel. Having established the structure of the new framework, the next step was to link the components of the behaviour system to the intervention functions and to link these to policy categories using the approach described in the Meth

### Top-2

- **Chunk ID:** `michie_2011_behaviour_change_wheel__0079`
- **Score:** `0.5961`
- **Document ID:** `michie_2011_behaviour_change_wheel`
- **Source:** `data/raw/michie_2011_behaviour_change_wheel.html`
- **Section:** `Discussion`
- **Text preview:** a range of theoretical approaches each of which independently addresses different aspects of the behaviour in question. The BCW is being developed into a theory- and evidence-based tool allowing a range of users to design and select interventions and policies according to an analysis of the nature of the behaviour, the mechanisms that need to be ch

### Top-3

- **Chunk ID:** `michie_2011_behaviour_change_wheel__0058`
- **Score:** `0.5939`
- **Document ID:** `michie_2011_behaviour_change_wheel`
- **Source:** `data/raw/michie_2011_behaviour_change_wheel.html`
- **Section:** `Development of a new framework`
- **Text preview:** Given that policies can only influence behaviour through the interventions that they enable or support, it seemed appropriate to place interventions between these and behaviour. The most parsimonious way of doing this seemed to be to represent the whole classification system in terms of a 'behaviour change wheel' (BCW) with three layers as shown in

**Comment:** Relevant. The retrieved chunks explain how the Behaviour Change Wheel links behaviour analysis, intervention functions, and policy categories.

---

## Query 4

**Query:** What are the predisposing, precipitating, and perpetuating factors in the 3P model?

### Top-1

- **Chunk ID:** `wright_2019_3p_disease_model__0016`
- **Score:** `0.6791`
- **Document ID:** `wright_2019_3p_disease_model`
- **Source:** `data/raw/wright_2019_3p_disease_model.html`
- **Section:** `Insomnia and the 3P Model`
- **Text preview:** [Spielman et al. (1987)](https://pmc.ncbi.nlm.nih.gov/articles/PMC6879427/#B104) and is colloquially known as “the 3P Model.” The three Ps – predisposing, precipitating, and perpetuating factors – all contribute to the development and maintenance of chronic insomnia. [Figure 1](https://pmc.ncbi.nlm.nih.gov/articles/PMC6879427/#F1) displays an adapt

### Top-2

- **Chunk ID:** `wright_2019_3p_disease_model__0104`
- **Score:** `0.6284`
- **Document ID:** `wright_2019_3p_disease_model`
- **Source:** `data/raw/wright_2019_3p_disease_model.html`
- **Section:** `Examples of 3P-Health Model Applications to Specific Diseases`
- **Text preview:** factors mentioned above, and the presence and specific type of perpetuating factors will vary from patient to patient. What would be important in an individual with no current perpetuating factors is a primary focus on the prevention and/or mitigation phases of the 3P model, depending on the “modifiability” of the relevant predisposing and precipit

### Top-3

- **Chunk ID:** `wright_2019_3p_disease_model__0113`
- **Score:** `0.5930`
- **Document ID:** `wright_2019_3p_disease_model`
- **Source:** `data/raw/wright_2019_3p_disease_model.html`
- **Section:** `Discussion and Implications for the Future`
- **Text preview:** integrated perspectives when studying, preventing, mitigating, or treating a variety of disease states and conditions. In terms of research, scientists might utilize the 3P disease model to conceptualize and identify actual predisposing, precipitating, and perpetuating factors for these and many other diseases. In this way, the model provides a fra

**Comment:** Relevant. Top-1 directly identifies the three factors, while Top-2 and Top-3 provide additional application and research context.

---

## Query 5

**Query:** How can stress affect physical health?

### Top-1

- **Chunk ID:** `ogden_2019_health_psychology__0135`
- **Score:** `0.7073`
- **Document ID:** `ogden_2019_health_psychology`
- **Source:** `data/raw/ogden_2019_health_psychology.pdf`
- **Section:** `Overview`
- **Text preview:** reasons that stress has been studied so consistently is because of its potential effect on the health of the individual. In particular, research shows a link between high-stress jobs and hypertension and coronary heart disease; higher life stress and physical symptoms; that stressful lives are associated with greater recurrence of colds and flu; an

### Top-2

- **Chunk ID:** `ogden_2019_health_psychology__0167`
- **Score:** `0.6415`
- **Document ID:** `ogden_2019_health_psychology`
- **Source:** `data/raw/ogden_2019_health_psychology.pdf`
- **Section:** `To Conclude`
- **Text preview:** Stress and pain are part of the continuum from health to illness and illustrate the key role of psychological factors in the processes involved in becoming ill. Stress is far more than a response to a stressor and in line with the transactional model of stress illustrates a role for appraisal. Stress can cause illness through either a direct pathwa

### Top-3

- **Chunk ID:** `ogden_2019_health_psychology__0136`
- **Score:** `0.6340`
- **Document ID:** `ogden_2019_health_psychology`
- **Source:** `data/raw/ogden_2019_health_psychology.pdf`
- **Section:** `Overview`
- **Text preview:** mortality by 17 years (266 participants had died). Stress can cause illness through either a direct or indirect pathway. The direct pathway involves stress-related changes in physiology such as raised blood pressure, raised heart rate, reduced immune function or cortisol production. The indirect pathway involves changes in health behaviors such as

**Comment:** Relevant. The retrieved chunks describe direct physiological pathways, indirect behavioural pathways, and links between stress and physical illness.

---

## Query 6

**Query:** What topics are covered in the Health Psychology course?

### Top-1

- **Chunk ID:** `ogden_2019_health_psychology__0245`
- **Score:** `0.6866`
- **Document ID:** `ogden_2019_health_psychology`
- **Source:** `data/raw/ogden_2019_health_psychology.pdf`
- **Section:** `Final Take-Home Message`
- **Text preview:** It has long been recognized that physical illness can have psychological consequences. This course has highlighted how psychology is relevant to all stages of illness from being well, to becoming ill, to being ill, and to health outcomes. Health psychology has a simple STORY which is often similar for different areas: “traditional models say health

### Top-2

- **Chunk ID:** `health_psychology_course_syllabus__0000`
- **Score:** `0.6764`
- **Document ID:** `health_psychology_course_syllabus`
- **Source:** `data/raw/course_syllabus.pdf`
- **Section:** `Document overview`
- **Text preview:** Syllabus for Introduction to Health Psychology Credits: 3 PSYC 1111 Instructor Contact Information: You can always send your instructor a private message through the Brightspace Messaging system, accessible via the envelope (Messages) icon in the top navigation bar. Once logged into your course, click your instructor’s profile page to see all the w

### Top-3

- **Chunk ID:** `ogden_2019_health_psychology__0005`
- **Score:** `0.6130`
- **Document ID:** `ogden_2019_health_psychology`
- **Source:** `data/raw/ogden_2019_health_psychology.pdf`
- **Section:** `The Background of Health Psychology`
- **Text preview:** Health psychology is the study of the role of psychology in any physical health problem including coughs and colds, cancer, coronary heart disease, HIV, obesity, and diabetes. It is best understood by comparing it to the more traditional biomedical model using 5 simple questions as follows:

**Comment:** Partially relevant. The syllabus appears in Top-2, but Top-1 and Top-3 provide broad descriptions of health psychology rather than a structured list of course topics.

---

# Overall Conclusion

The baseline semantic retrieval layer performs well for focused conceptual questions about named models and clearly defined health psychology topics.

Retrieval is weaker for broader navigational questions and questions that require a precise list from a specific source. The current system uses semantic vector similarity only and does not apply metadata filtering, hybrid retrieval, reranking, or query rewriting.
