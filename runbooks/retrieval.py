import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Runbook

logger = logging.getLogger(__name__)

# Configurable minimum match threshold. Similarity score must be >= 0.20 to recommend.
MIN_MATCH_SCORE = 0.20

def generate_citation(incident, runbook, match_score):
    """
    Extracts concrete evidence and citation metadata linking the incident to the recommended runbook.
    """
    import re
    incident_text = f"{incident.title} {incident.description} {getattr(incident, 'intent', '')} {getattr(incident, 'service', '')}".lower()
    raw_symptoms = [s.strip() for s in runbook.symptoms.splitlines() if s.strip()]
    
    # Identify symptoms whose keywords overlap with the incident description
    matched_symptoms = []
    for s in raw_symptoms:
        words = [w.lower() for w in re.findall(r'\b[a-zA-Z]{3,}\b', s) if w.lower() not in {'with', 'from', 'this', 'that', 'have', 'been'}]
        if any(w in incident_text for w in words):
            matched_symptoms.append(s)

    if not matched_symptoms and raw_symptoms:
        matched_symptoms = raw_symptoms[:2]

    steps_list = [step.strip() for step in runbook.steps.splitlines() if step.strip()]
    relevant_steps = steps_list[:3] if steps_list else ["Follow standard procedure steps."]

    category_match = (runbook.category == getattr(incident, 'category', ''))

    return {
        "runbook_number": runbook.runbook_number,
        "title": runbook.title,
        "match_score": match_score,
        "match_score_percentage": round(match_score * 100, 2),
        "matched_category": runbook.get_category_display(),
        "category_match": category_match,
        "matched_symptoms": matched_symptoms,
        "evidence_symptoms": raw_symptoms[0] if raw_symptoms else runbook.description,
        "relevant_steps": relevant_steps,
        "citation_reference": runbook.runbook_number
    }


def retrieve_best_runbook(incident, actor=None):
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
            try:
                from incidents.models import Incident
                from automation.audit import create_audit_log
                from automation.models import AuditLog
                if isinstance(incident, Incident):
                    create_audit_log(
                        incident=incident,
                        event_type=AuditLog.EventType.AI_ANALYSIS_COMPLETED,
                        message="Local NLP analysis completed. No active runbooks available.",
                        actor=actor
                    )
            except Exception:
                pass
            return {
                "runbook": None,
                "score": 0.0,
                "match_score": 0.0,
                "matched_category": None,
                "matched_symptoms": [],
                "citation_reference": None,
                "citation": {},
                "top_matches": []
            }

        # 2. Build incident search text (combining title, description, category, and normalized fields)
        intent_info = getattr(incident, 'intent', '')
        service_info = getattr(incident, 'service', '')
        incident_text = f"{incident.title} {incident.description} {incident.category} {intent_info} {service_info}".strip()

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

        # Phase 8: Record AI Analysis Completed audit event
        try:
            from incidents.models import Incident
            from automation.audit import create_audit_log
            from automation.models import AuditLog
            if isinstance(incident, Incident):
                create_audit_log(
                    incident=incident,
                    event_type=AuditLog.EventType.AI_ANALYSIS_COMPLETED,
                    message="Local NLP analysis completed for the incident.",
                    actor=actor
                )
        except Exception as audit_err:
            logger.warning(f"Could not record AI_ANALYSIS_COMPLETED audit: {str(audit_err)}")

        # 9. Evaluate best match against threshold
        if matches and matches[0][1] >= MIN_MATCH_SCORE:
            best_match, best_score = matches[0]
            inc_id = getattr(incident, 'incident_number', 'INC-UNKNOWN')
            logger.info(f"[{inc_id}] Retrieved runbook {best_match.runbook_number} (score: {best_score:.2f})")
            
            # Generate structured citations and evidence
            citation = generate_citation(incident, best_match, best_score)

            # Phase 8: Record Runbook Recommended audit event
            try:
                from incidents.models import Incident
                from automation.audit import create_audit_log
                from automation.models import AuditLog
                if isinstance(incident, Incident):
                    create_audit_log(
                        incident=incident,
                        event_type=AuditLog.EventType.RUNBOOK_RECOMMENDED,
                        message=f"Runbook '{best_match.title}' recommended with a match score of {best_score * 100:.1f}%.",
                        actor=actor,
                        metadata={
                            "runbook_id": best_match.id,
                            "runbook_number": best_match.runbook_number,
                            "runbook_title": best_match.title,
                            "match_score": best_score,
                            "citation_reference": citation["citation_reference"],
                            "matched_category": citation["matched_category"],
                            "matched_symptoms": citation["matched_symptoms"]
                        }
                    )
            except Exception as audit_err:
                logger.warning(f"Could not record RUNBOOK_RECOMMENDED audit: {str(audit_err)}")


            return {
                "runbook": best_match,
                "score": best_score,
                "match_score": best_score,
                "matched_category": citation["matched_category"],
                "matched_symptoms": citation["matched_symptoms"],
                "citation_reference": citation["citation_reference"],
                "citation": citation,
                "top_matches": top_matches
            }
        else:
            logger.info("AI retrieval failed: best match score is below minimum threshold.")
            return {
                "runbook": None,
                "score": 0.0,
                "match_score": 0.0,
                "matched_category": None,
                "matched_symptoms": [],
                "citation_reference": None,
                "citation": {},
                "top_matches": top_matches
            }

    except Exception as e:
        logger.error(f"Error executing AI Runbook Retrieval: {str(e)}", exc_info=True)
        return {
            "runbook": None,
            "score": 0.0,
            "match_score": 0.0,
            "matched_category": None,
            "matched_symptoms": [],
            "citation_reference": None,
            "citation": {},
            "top_matches": []
        }

# Backward compatibility / semantic alias
retrieve_runbooks_for_incident = retrieve_best_runbook

