from typing import Dict

# Authority Registry for ARES_POC
# Defines credibility weights W(E) for recognized authoritative sources.

# Institutional & Global Governance (1.0)
INSTITUTIONAL_DOMAINS = {
    "pib.gov.in": "Press Information Bureau (Govt of India)",
    "data.gov.in": "Open Government Data (OGD) Platform India",
    "who.int": "World Health Organization",
    "un.org": "United Nations",
    "worldbank.org": "World Bank",
    "eci.gov.in": "Election Commission of India",
    "sci.gov.in": "Supreme Court of India",
    "nasa.gov": "NASA",
    "esa.int": "European Space Agency",
    "cdc.gov": "Centers for Disease Control and Prevention",
    "nih.gov": "National Institutes of Health"
}

# Professional Fact-Checking Organizations (0.95)
FACT_CHECKER_DOMAINS = {
    "altnews.in": "Alt News",
    "boomlive.in": "BOOM Live",
    "factly.in": "Factly",
    "snopes.com": "Snopes",
    "politifact.com": "PolitiFact",
    "fullfact.org": "Full Fact"
}

# Reputed News Agencies & Academic Journals (0.9)
REPUTED_NEWS_DOMAINS = {
    "reuters.com": "Reuters",
    "apnews.com": "Associated Press",
    "bbc.com": "BBC News",
    "thehindu.com": "The Hindu",
    "indianexpress.com": "The Indian Express",
    "aljazeera.com": "Al Jazeera",
    "nature.com": "Nature Journal",
    "science.org": "Science Magazine",
    "thelancet.com": "The Lancet"
}

def get_authority_weight(domain: str) -> float:
    """Returns the research-grade weight W(E) for a given domain."""
    if domain in INSTITUTIONAL_DOMAINS:
        return 1.0
    if domain in FACT_CHECKER_DOMAINS:
        return 0.95
    if domain in REPUTED_NEWS_DOMAINS:
        return 0.9
    return None # Fallback to generic TLD/keyword logic
