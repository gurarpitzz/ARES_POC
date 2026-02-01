from urllib.parse import urlparse
from authority_registry import get_authority_weight

class CredibilityWeight:
    def __init__(self):
        # Fallback patterns for domains not in the explicit Registry
        self.trusted_tlds = ['.gov', '.edu', '.org', '.ac.uk', '.int', '.mil']
        self.news_keywords = ['news', 'reuters', 'apnews', 'bbc', 'nytimes', 'theguardian', 'npr']
        self.blog_keywords = ['blog', 'medium.com', 'substack', 'wordpress', 'blogspot']

    def calculate(self, url: str) -> float:
        """
        W(E) = Weight based on source domain.
        1. Checks Authority Registry (Explicit Mapping)
        2. Checks TLDs (Categorical Fallback)
        3. Checks Keywords (Generic Fallback)
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        if domain.startswith("www."):
            domain = domain[4:]
        
        # 1. Authority Registry Check (Highest Precision)
        registry_weight = get_authority_weight(domain)
        if registry_weight is not None:
            return registry_weight
            
        # 2. Categorical TLD Check
        if any(domain.endswith(tld) for tld in self.trusted_tlds):
            return 1.0
            
        # 3. News Keyword Check
        if any(kw in domain for kw in self.news_keywords):
            return 0.9 # Aligned with Registry News weight
            
        # 4. Blog Check
        if any(kw in domain for kw in self.blog_keywords):
            return 0.6
            
        # 5. Default/Unknown
        return 0.4

if __name__ == "__main__":
    cw = CredibilityWeight()
    urls = [
        "https://www.nasa.gov/science-mission-directorate/moon-mission",
        "https://www.nytimes.com/2023/01/01/science/moon.html",
        "https://myblog.wordpress.com/post1",
        "https://random-site.xyz/article"
    ]
    for u in urls:
        print(f"URL: {u} | Weight: {cw.calculate(u)}")
