import requests
import re
from bs4 import BeautifulSoup
from ddgs import DDGS
from typing import List, Dict
import hashlib
import json
import os

class Retriever:
    def __init__(self, k: int = 10, mode: str = "web", cache_dir: str = "cache"):
        self.k = k
        self.mode = mode
        self.cache_dir = cache_dir
        # No pre-initialization needed as we use context manager in _retrieve_web
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def retrieve(self, claim: str, local_data: List[Dict] = None) -> List[Dict[str, str]]:
        """
        R(C) operator with multi-backend support and caching for determinism.
        """
        cache_key = hashlib.md5(f"{self.mode}_{claim}".encode()).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as f:
                return json.load(f)

        if self.mode == "wiki":
            # R_wiki(C) - Simulated or Local Wiki search
            results = self._retrieve_local(claim, local_data)
        elif self.mode == "liar":
            # R_liar(C) - Local data retrieval
            results = self._retrieve_local(claim, local_data)
        else:
            # R_web(C) - Web search
            results = self._retrieve_web(claim)

        # Ensure deterministic order by text
        results.sort(key=lambda x: x['text'])
        
        # Save to cache
        with open(cache_path, 'w') as f:
            json.dump(results, f)
            
        return results

    def _retrieve_web(self, claim: str) -> List[Dict[str, str]]:
        results = []
        try:
            # Research Integrity: Use neutral query without source bias
            # Let W(E) handle the credibility weighting in the truth functional
            with DDGS() as ddgs:
                search_results = list(ddgs.text(claim, max_results=self.k))
            
            for result in search_results:
                url = result['href']
                try:
                    content = self._scrape_url(url)
                    passages = self._split_into_passages(content)
                    for p in passages:
                        results.append({
                            'url': url,
                            'text': p,
                            'source': result.get('title', 'Unknown')
                        })
                except Exception:
                    pass
        except Exception as e:
            print(f"[ERROR] Retrieval failed: {e}")
        return results

    def _retrieve_local(self, claim: str, data: List[Dict]) -> List[Dict[str, str]]:
        # In research datasets like FEVER, data is often pre-associated or requires a separate index.
        # For POC, if local_data is provided (from evaluate.py), we use it.
        if data:
            return data
        return []

    def _scrape_url(self, url: str) -> str:
        # Existing scraping logic remains similar but more robust
        try:
            headers = {
                "User-Agent": "ARES-POC Research Bot (academic project)"
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            for script in soup(["script", "style"]):
                script.decompose()
            return soup.get_text()
        except:
            return ""

    def _split_into_passages(self, text: str) -> List[str]:
        # Sentence-level splitting for better entailment sensitivity
        # Regex splits by sentence endings followed by spaces
        sentences = re.split(r'(?<=[.!?]) +', text.replace('\n', ' '))
        # Filter for meaningful length and return top sentences
        return [s.strip() for s in sentences if len(s.strip()) > 40][:10]

if __name__ == "__main__":
    retriever = Retriever(k=3)
    c = "The moon is made of green cheese."
    evidences = retriever.retrieve(c)
    print(f"Retrieved {len(evidences)} passages.")
    for e in evidences[:3]:
        print(f"Source: {e['url']}\nText: {e['text'][:100]}...\n")
