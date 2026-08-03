
import json
import re
from pathlib import Path

import faiss
from sentence_transformers import SentenceTransformer


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CHUNKS_PATH = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "chunks_for_retrieval.jsonl"
)

INDEX_PATH = (
    PROJECT_ROOT
    / "index"
    / "faiss.index"
)

OUTPUTS_DIR = PROJECT_ROOT / "outputs"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

TOP_K = 3
CANDIDATE_K = 10
FINAL_K = 3

SEMANTIC_WEIGHT = 0.7
KEYWORD_WEIGHT = 0.3


DOCUMENT_TYPE_BY_DOCUMENT = {
    "health_psychology_course_syllabus": "syllabus",
    "ogden_2019_health_psychology": "textbook",
    "michie_2011_behaviour_change_wheel": "research_article",
    "wright_2019_3p_disease_model": "research_article",
}


TEST_QUERIES = [
    {
        "query": "What is the biopsychosocial model of health?",
        "expected_document": "ogden_2019_health_psychology",
        "metadata_filter": {
            "document_type": "textbook",
        },
    },
    {
        "query": "What are the components of the COM-B model?",
        "expected_document": "michie_2011_behaviour_change_wheel",
        "metadata_filter": {
            "document_type": "research_article",
        },
    },
    {
        "query": (
            "How does the Behaviour Change Wheel "
            "support intervention design?"
        ),
        "expected_document": "michie_2011_behaviour_change_wheel",
        "metadata_filter": {
            "document_type": "research_article",
        },
    },
    {
        "query": (
            "What are the predisposing, precipitating, "
            "and perpetuating factors in the 3P model?"
        ),
        "expected_document": "wright_2019_3p_disease_model",
        "metadata_filter": {
            "document_type": "research_article",
        },
    },
    {
        "query": "How can stress affect physical health?",
        "expected_document": "ogden_2019_health_psychology",
        "metadata_filter": {
            "document_type": "textbook",
        },
    },
    {
        "query": (
            "What topics are covered in the "
            "Health Psychology course?"
        ),
        "expected_document": "health_psychology_course_syllabus",
        "metadata_filter": {
            "document_type": "syllabus",
        },
    },
]


def load_jsonl(path):
    records = []

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        for line in file:
            records.append(json.loads(line))

    return records


def add_metadata(chunks):
    for chunk in chunks:
        document_id = chunk["document_id"]

        chunk["metadata"] = {
            "document_id": document_id,
            "source_file": chunk.get("source_file"),
            "section": chunk.get("section"),
            "chunk_index": chunk.get("chunk_index"),
            "document_type": (
                DOCUMENT_TYPE_BY_DOCUMENT[document_id]
            ),
        }


def semantic_search(
    query,
    model,
    index,
    chunks,
    top_k,
):
    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
    )

    query_embedding = query_embedding.astype(
        "float32"
    )

    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(
        query_embedding,
        top_k,
    )

    results = []

    for score, chunk_index in zip(
        scores[0],
        indices[0],
    ):
        if chunk_index == -1:
            continue

        chunk = chunks[chunk_index]

        results.append(
            {
                "score": float(score),
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "metadata": chunk["metadata"],
            }
        )

    return results


def metadata_matches(
    result,
    metadata_filter,
):
    metadata = result.get("metadata", {})

    for key, expected_value in metadata_filter.items():
        if metadata.get(key) != expected_value:
            return False

    return True


def apply_metadata_filter(
    results,
    metadata_filter,
):
    return [
        result
        for result in results
        if metadata_matches(
            result,
            metadata_filter,
        )
    ]


def tokenize(text):
    return set(
        re.findall(
            r"\b\w+\b",
            text.lower(),
        )
    )


def keyword_overlap_score(query, text):
    query_terms = tokenize(query)
    text_terms = tokenize(text)

    if not query_terms:
        return 0.0

    shared_terms = query_terms.intersection(
        text_terms
    )

    return len(shared_terms) / len(query_terms)


def add_hybrid_scores(query, results):
    hybrid_results = []

    for result in results:
        keyword_score = keyword_overlap_score(
            query,
            result["text"],
        )

        hybrid_score = (
            SEMANTIC_WEIGHT * result["score"]
            + KEYWORD_WEIGHT * keyword_score
        )

        hybrid_result = result.copy()
        hybrid_result["keyword_score"] = keyword_score
        hybrid_result["hybrid_score"] = hybrid_score

        hybrid_results.append(hybrid_result)

    hybrid_results.sort(
        key=lambda result: result["hybrid_score"],
        reverse=True,
    )

    return hybrid_results


def calculate_metrics(evaluations):
    top_1_correct = 0
    recall_at_3 = 0

    for evaluation in evaluations:
        expected_document = (
            evaluation["expected_document"]
        )

        retrieved_documents = [
            result["metadata"].get("document_id")
            for result in evaluation["results"]
        ]

        if (
            retrieved_documents
            and retrieved_documents[0]
            == expected_document
        ):
            top_1_correct += 1

        if expected_document in retrieved_documents:
            recall_at_3 += 1

    total_queries = len(evaluations)

    return {
        "top_1_accuracy": (
            top_1_correct / total_queries
        ),
        "recall_at_3": (
            recall_at_3 / total_queries
        ),
    }


def main():
    OUTPUTS_DIR.mkdir(exist_ok=True)

    chunks = load_jsonl(CHUNKS_PATH)
    add_metadata(chunks)

    index = faiss.read_index(
        str(INDEX_PATH)
    )

    model = SentenceTransformer(
        MODEL_NAME
    )

    baseline_results = []
    improved_results = []

    for test_case in TEST_QUERIES:
        query = test_case["query"]
        expected_document = (
            test_case["expected_document"]
        )
        metadata_filter = (
            test_case["metadata_filter"]
        )

        baseline = semantic_search(
            query=query,
            model=model,
            index=index,
            chunks=chunks,
            top_k=TOP_K,
        )

        candidates = semantic_search(
            query=query,
            model=model,
            index=index,
            chunks=chunks,
            top_k=CANDIDATE_K,
        )

        filtered_candidates = apply_metadata_filter(
            results=candidates,
            metadata_filter=metadata_filter,
        )

        ranked_candidates = add_hybrid_scores(
            query=query,
            results=filtered_candidates,
        )

        improved = ranked_candidates[:FINAL_K]

        baseline_results.append(
            {
                "query": query,
                "expected_document": expected_document,
                "results": baseline,
            }
        )

        improved_results.append(
            {
                "query": query,
                "expected_document": expected_document,
                "metadata_filter": metadata_filter,
                "results": improved,
            }
        )

        print("=" * 80)
        print("Query:", query)
        print(
            "Baseline top-1:",
            baseline[0]["chunk_id"],
        )
        print(
            "Improved top-1:",
            improved[0]["chunk_id"],
        )
        print()

    baseline_metrics = calculate_metrics(
        baseline_results
    )

    improved_metrics = calculate_metrics(
        improved_results
    )

    baseline_output_path = (
        OUTPUTS_DIR
        / "baseline_results.json"
    )

    improved_output_path = (
        OUTPUTS_DIR
        / "improved_results.json"
    )

    baseline_output_path.write_text(
        json.dumps(
            baseline_results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    improved_output_path.write_text(
        json.dumps(
            improved_results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print("Baseline Top-1 accuracy:", end=" ")
    print(
        f"{baseline_metrics['top_1_accuracy']:.1%}"
    )

    print("Baseline Recall@3:", end=" ")
    print(
        f"{baseline_metrics['recall_at_3']:.1%}"
    )

    print("Improved Top-1 accuracy:", end=" ")
    print(
        f"{improved_metrics['top_1_accuracy']:.1%}"
    )

    print("Improved Recall@3:", end=" ")
    print(
        f"{improved_metrics['recall_at_3']:.1%}"
    )

    print()
    print("Saved:", baseline_output_path)
    print("Saved:", improved_output_path)


if __name__ == "__main__":
    main()
