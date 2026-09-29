"""
Ticket Ingestion & Normalization Layer.

This module provides deterministic, rule-based classification and text normalization
for incident tickets without calling external AI APIs or large language models.
"""

import re

# Deterministic keyword patterns for Intent Classification
INTENT_PATTERNS = [
    (
        "Service Outage",
        [
            r"\b(outage|down|unavailable|crashed|stopped|dead|offline|unresponsive|503|502|500)\b",
            r"\b(cannot connect|not responding|service halted|system down|connection refused)\b",
            r"\b(server is down|site is down|app is down|completely down)\b"
        ]
    ),
    (
        "Service Degradation",
        [
            r"\b(slow|sluggish|degraded|latency|lag|high load|spike|bottleneck|performance issue)\b",
            r"\b(taking too long|very slow|high cpu|high memory|memory leak|timing out|timeouts)\b",
            r"\b(slow since|response time)\b"
        ]
    ),
    (
        "Access Issue",
        [
            r"\b(login|authentication|auth|permission|forbidden|unauthorized|access denied|credentials)\b",
            r"\b(password|token expired|sso|ldap|ssl cert|certificate expired|tls handshake|403)\b"
        ]
    ),
    (
        "Database Issue",
        [
            r"\b(database|postgres|postgresql|mysql|sqlite|sql|query|deadlock|db connection)\b",
            r"\b(max connections|db pool|database error|corrupt table)\b"
        ]
    ),
    (
        "Network Issue",
        [
            r"\b(network|dns|packet loss|ping|gateway|unreachable|subnet|router|switch|wifi)\b",
            r"\b(name resolution|cannot resolve|host not found|connection drop)\b"
        ]
    ),
    (
        "Storage Issue",
        [
            r"\b(disk|storage|no space|space full|filesystem|partition|volume|inode|out of disk)\b",
            r"\b(low storage|disk usage)\b"
        ]
    ),
    (
        "Configuration Issue",
        [
            r"\b(config|configuration|syntax error|misconfigured|settings|env var|parameter)\b",
            r"\b(bad config|invalid setting)\b"
        ]
    )
]

# Deterministic keyword patterns for Service Classification
SERVICE_PATTERNS = [
    (
        "Web Server",
        [
            r"\b(nginx|apache|httpd|web server|webserver|website|web page|url|http|https)\b"
        ]
    ),
    (
        "Database",
        [
            r"\b(database|postgres|postgresql|mysql|mariadb|sqlite|db|query|relational)\b"
        ]
    ),
    (
        "Network",
        [
            r"\b(network|dns|domain|gateway|subnet|ping|ip|connectivity|packet|lan|wan)\b"
        ]
    ),
    (
        "Storage",
        [
            r"\b(disk|storage|drive|volume|mount|filesystem|hard drive|inodes|partition)\b"
        ]
    ),
    (
        "Authentication",
        [
            r"\b(auth|login|sso|ldap|certificate|ssl|tls|token|credentials|password)\b"
        ]
    ),
    (
        "Application",
        [
            r"\b(application|app|api|django|service|backend|frontend|cache|redis|process)\b"
        ]
    )
]

# Category fallback mapping from Incident.Category
CATEGORY_SERVICE_MAP = {
    "SERVER": "Web Server",
    "DATABASE": "Database",
    "NETWORK": "Network",
    "STORAGE": "Storage",
    "SECURITY": "Authentication",
    "APPLICATION": "Application",
    "OTHER": "Unknown"
}


def classify_intent(text):
    """
    Identifies intent from text using deterministic keyword matching.
    """
    clean_text = text.lower()
    for intent, patterns in INTENT_PATTERNS:
        for pat in patterns:
            if re.search(pat, clean_text):
                return intent
    return "Unknown"


def classify_service(text, fallback_category=None):
    """
    Identifies the affected technical service from text with category fallback.
    """
    clean_text = text.lower()
    for service, patterns in SERVICE_PATTERNS:
        for pat in patterns:
            if re.search(pat, clean_text):
                return service

    if fallback_category and fallback_category in CATEGORY_SERVICE_MAP:
        mapped = CATEGORY_SERVICE_MAP[fallback_category]
        if mapped != "Unknown":
            return mapped

    return "Unknown"


def classify_priority(intent, service, text):
    """
    Computes suggested priority (P1, P2, P3, P4) based on intent severity, affected service, and urgency cues.
    P1: Critical Outage / Complete service disruption
    P2: High Impact / Degradation on critical systems / Major functionality down
    P3: Moderate Impact / Degradation or localized issue
    P4: Minor / Low impact / Configuration or informational
    """
    clean_text = text.lower()

    # Explicit critical indicators
    if re.search(r"\b(critical|emergency|entire system|all users|production down|catastrophic)\b", clean_text):
        return "P1"

    if intent == "Service Outage":
        if service in ["Web Server", "Database", "Authentication"]:
            return "P1"
        return "P2"

    if intent == "Service Degradation":
        if service in ["Web Server", "Database"]:
            return "P2"
        return "P3"

    if intent in ["Database Issue", "Storage Issue"]:
        if "full" in clean_text or "cannot connect" in clean_text:
            return "P2"
        return "P3"

    if intent == "Access Issue":
        if "sso" in clean_text or "all users" in clean_text:
            return "P2"
        return "P3"

    if intent == "Configuration Issue":
        return "P4"

    return "P3"


def generate_normalized_description(intent, service, raw_description, raw_title=""):
    """
    Synthesizes a standardized problem description from raw user input.
    Cleans colloquial phrasing, extracts core issue, and structures formal description.
    """
    raw_combined = f"{raw_title}. {raw_description}".strip()
    
    # Clean redundant casual phrases like "pls check", "help asap", "since morning"
    cleaned = re.sub(r"(?i)\b(pls|please|kindly|asap|urgent|check|fix|bro|team)\b", "", raw_combined)
    cleaned = re.sub(r"\s+", " ", cleaned).strip(" .:")

    if intent != "Unknown" and service != "Unknown":
        if intent == "Service Degradation":
            return f"{service} response time or performance has degraded. Summary: {cleaned}."
        elif intent == "Service Outage":
            return f"{service} is unavailable or unresponsive. Summary: {cleaned}."
        elif intent == "Access Issue":
            return f"Authentication or authorization failure affecting {service}. Summary: {cleaned}."
        elif intent == "Database Issue":
            return f"Database connectivity or execution anomaly reported. Summary: {cleaned}."
        elif intent == "Network Issue":
            return f"Network connectivity or resolution impairment reported. Summary: {cleaned}."
        elif intent == "Storage Issue":
            return f"Storage capacity or filesystem issue reported. Summary: {cleaned}."
        elif intent == "Configuration Issue":
            return f"Configuration discrepancy or parameter error observed. Summary: {cleaned}."

    return f"Incident reported on {service} with intent '{intent}'. Summary: {cleaned}."


def normalize_incident_data(title, description, category=None):
    """
    Main normalization entry point.
    Returns structured dictionary with intent, service, priority, and normalized description.
    """
    full_text = f"{title or ''} {description or ''}"
    intent = classify_intent(full_text)
    service = classify_service(full_text, fallback_category=category)
    classified_prio = classify_priority(intent, service, full_text)
    normalized_desc = generate_normalized_description(intent, service, description, raw_title=title)

    return {
        "intent": intent,
        "service": service,
        "classified_priority": classified_prio,
        "normalized_description": normalized_desc,
        "classification_method": "Rule-based local classification"
    }
