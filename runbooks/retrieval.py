import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Runbook

logger = logging.getLogger(__name__)

# Configurable minimum match threshold. Similarity score must be >= 0.20 to recommend.
MIN_MATCH_SCORE = 0.20

def retrieve_best_runbook(incident):
    """
    NLP Retrieval Service.
    Compares the Incident (title, description, category) against the active Runbook Knowledge Base.
    
    TF-IDF (Term Frequency-Inverse Document Frequency):
    Measures word importance across the corpus, penalizing generic stop words while elevating specific technical terms.
    
    Cosine Similarity:
    Calculates the cosine of the angle between the vector representation of the incident and each runbook.
    Values range from 0.0 (entirely orthogonal/unrelated) to 1.0 (identical terms).
    """
    try:
        # 1. Fetch only active runbooks
        active_runbooks = list(Runbook.objects.filter(is_active=True))
        if not active_runbooks:
            logger.warning("No active runbooks found in the database. Skipping retrieval.")
            return {
                "runbook": None,
                "score": 0.0,
                "top_matches": []
            }

        # 2. Build incident search text (combining title, description, category)
        incident_text = f"{incident.title} {incident.description} {incident.category}"

        # 3. Build runbook corpus texts using title, description, symptoms, and category
        runbook_texts = []
        for rb in active_runbooks:
            combined_text = f"{rb.title} {rb.description} {rb.symptoms} {rb.category}"
            runbook_texts.append(combined_text)

        # 4. Construct the corpus by appending the incident text to the runbook texts
        corpus = runbook_texts + [incident_text]

        # 5. Fit TfidfVectorizer on the complete corpus
        vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(corpus)

        # 6. Extract vectors: 
        # - The runbook vectors correspond to the first N rows
        # - The incident vector is the last row in the matrix
        runbook_vectors = tfidf_matrix[:-1]
        incident_vector = tfidf_matrix[-1]

        # 7. Compute Cosine Similarity between incident and all runbooks
        similarities = cosine_similarity(incident_vector, runbook_vectors)[0]

        # 8. Pair each runbook with its score, filter and sort
        matches = []
        for index, score in enumerate(similarities):
            matches.append((active_runbooks[index], float(score)))

        # Sort matches descending by score
        matches.sort(key=lambda x: x[1], reverse=True)

        # Keep top 3 alternative matches for diagnostic output
        top_matches = matches[:3]

        # 9. Evaluate best match against threshold
        if matches and matches[0][1] >= MIN_MATCH_SCORE:
            best_match, best_score = matches[0]
            logger.info(f"AI retrieval successfully matched incident to {best_match.runbook_number} (Score: {best_score:.4f})")
            return {
                "runbook": best_match,
                "score": best_score,
                "top_matches": top_matches
            }
        else:
            logger.info("AI retrieval failed: best match score is below minimum threshold.")
            return {
                "runbook": None,
                "score": 0.0,
                "top_matches": top_matches
            }

    except Exception as e:
        logger.error(f"Error executing AI Runbook Retrieval: {str(e)}", exc_info=True)
        return {
            "runbook": None,
            "score": 0.0,
            "top_matches": []
        }
