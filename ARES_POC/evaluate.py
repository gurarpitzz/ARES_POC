import argparse
import pandas as pd
from verifier import Verifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import time
import json
import glob
import os

WIKI_INDEX = {}

def build_wiki_index(path="wiki-pages/"):
    """
    Research Utility: Indexes the FEVER Wikipedia dump (jsonl files).
    Expected format: {"id": "Page_Title", "text": "Sentence 0\nSentence 1..."}
    """
    if not os.path.exists(path):
        print(f"WARNING: Wiki path {path} not found. Skipping real index build.")
        return
        
    print(f"Building Wiki Index from {path}...")
    for file in glob.glob(os.path.join(path, "*.jsonl")):
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    sentences = obj["text"].split("\n")
                    WIKI_INDEX[obj["id"]] = sentences
                except:
                    continue
    print(f"Index built: {len(WIKI_INDEX)} pages loaded.")

def load_wiki_sentence(page_title, line_id):
    """
    Retrieves the exact gold sentence from the loaded Wikipedia index.
    """
    try:
        # FEVER page_titles in index match the 'id' field
        sentences = WIKI_INDEX.get(page_title, [])
        if line_id < len(sentences):
            return sentences[line_id]
        return ""
    except:
        return ""

# load_wiki_sentence replaced by indexed version above

def extract_fever_evidence(item):
    """
    Extracts the REAL gold evidence passages as defined by the FEVER protocol.
    FEVER evidence format: [ [ [ann_id, ev_id, page, line], ... ], [set2], ... ]
    """
    passages = []
    
    # FEVER items have an 'evidence' field which is a list of lists of evidence sets.
    # picking the first non-empty set.
    if 'evidence' in item and item['evidence']:
        evidence_set = []
        for s in item['evidence']:
            if s:
                evidence_set = s
                break
                
        for annotation in evidence_set:
            wiki_page = annotation[2]
            line_id = annotation[3]
            
            if wiki_page and line_id is not None:
                text = load_wiki_sentence(wiki_page, line_id)
                # Guard: Only real, non-empty sentences enter the pipeline
                if text.strip():
                    passages.append({
                        'text': text, 
                        'url': f'wikipedia://{wiki_page}#L{line_id}'
                     })
                
    return passages

def evaluate_fever(verifier, num_samples=50):
    print(f"Evaluating on FEVER (sample size: {num_samples}) - ISOLATED FUNCTIONAL MODE")
    try:
        # Research Mirror for FEVER train data (v1.0)
        url = "https://fever.ai/data/train.jsonl"
        df = pd.read_json(url, lines=True, chunksize=num_samples)
        samples_df = next(df)
    except Exception as e:
        print(f"USING LOCAL FALLBACK for FEVER verification logic (Remote failed: {e})")
        # FEVER evaluation requires gold passages. If remote fails, we use a structured fallback for logical verification.
        samples_df = pd.DataFrame([
            {
                "claim": "The Earth is flat.",
                "label": "REFUTES",
                "evidence": [[ [0,0,"Flat_Earth",0] ]] # Reference to index
            },
            {
                "claim": "The moon orbits the Earth.",
                "label": "SUPPORTS",
                "evidence": [[ [0,0,"Moon",0] ]]
            }
        ])
    
    y_true = []
    y_pred = []
    
    # Iterate through samples
    for _, item in samples_df.iterrows():
        claim = item['claim']
        label = item['label']
        
        target = "UNCERTAIN"
        # FEVER Labels: SUPPORTS, REFUTES, NOT_ENOUGH_INFO
        if label == "SUPPORTS" or label == 0: target = "VERIFIED"
        elif label == "REFUTES" or label == 1: target = "MISINFORMATION"
        elif label == "NOT_ENOUGH_INFO" or label == 2: target = "UNCERTAIN"
        
        y_true.append(target)
        gold_passages = extract_fever_evidence(item)
        
        if not gold_passages:
            y_pred.append("UNCERTAIN")
            print(f"Claim: {claim[:50]}... | True: {target} | Pred: UNCERTAIN (No gold evidence)")
            continue
            
        result = verifier.verify_with_evidence(claim, gold_passages)
        y_pred.append(result['verdict'])
        print(f"Claim: {claim[:50]}... | True: {target} | Pred: {result['verdict']}")

    return calculate_metrics(y_true, y_pred)

def evaluate_liar(verifier, num_samples=50):
    print(f"Evaluating on LIAR (sample size: {num_samples})...")
    try:
        # LIAR Official TSV Mirror (raw format)
        url = "https://raw.githubusercontent.com/Tariq60/LIAR-Dataset/master/train.tsv"
        df = pd.read_csv(url, sep='\t', header=None, usecols=[1, 2], names=['label', 'statement'])
        samples_df = df.sample(n=num_samples, random_state=42)
    except Exception as e:
        print(f"USING LOCAL FALLBACK for LIAR (Remote failed: {e})")
        samples_df = pd.DataFrame([
            {"label": "false", "statement": "The Earth is flat."},
            {"label": "true", "statement": "Water freezes at zero degrees Celsius."}
        ])
    
    y_true = []
    y_pred = []
    
    for _, item in samples_df.iterrows():
        claim = item['statement']
        label = item['label']
        
        target = "UNCERTAIN"
        if label in ["true", "mostly-true", 2, 3]: target = "VERIFIED"
        elif label in ["false", "pants-fire", 0, 5]: target = "MISINFORMATION"
        
        y_true.append(target)
        result = verifier.verify(claim)
        y_pred.append(result['verdict'])
        print(f"Claim: {claim[:50]}... | True: {target} | Pred: {result['verdict']}")

    return calculate_metrics(y_true, y_pred)

def calculate_metrics(y_true, y_pred):
    labels = ["VERIFIED", "MISINFORMATION", "UNCERTAIN"]
    acc = accuracy_score(y_true, y_pred)
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', labels=labels)
    
    return {
        "accuracy": acc,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }

def main():
    parser = argparse.ArgumentParser(description="Evaluate ARES_POC on benchmarks")
    parser.add_argument("--dataset", type=str, choices=["fever", "liar", "both"], default="both")
    parser.add_argument("--samples", type=int, default=5)
    
    args = parser.parse_args()
    
    # Initialize Wiki Index for FEVER
    build_wiki_index("wiki-pages/")
    
    if args.dataset in ["fever", "both"] and not WIKI_INDEX:
        print("ERROR: FEVER wiki index not loaded. Evaluation invalid.")
        print("Please ensure Wikipedia JSONL files are in 'wiki-pages/' directory.")
        return
    
    # Ablation Study Configurations (Tuning k and M)
    configs = [
        {"k": 5, "m": 3},
        {"k": 10, "m": 5},
        {"k": 10, "m": 10},
    ]
    
    all_results = []
    
    for config in configs:
        print(f"\n>>> Running configuration: k={config['k']}, m={config['m']}")
        
        row = {"k": config['k'], "m": config['m']}
        
        if args.dataset in ["fever", "both"]:
            verifier = Verifier(k=config['k'], m=config['m'], mode="wiki")
            fever_res = evaluate_fever(verifier, args.samples)
            row["fever_f1"] = fever_res['f1']
            
        if args.dataset in ["liar", "both"]:
            verifier = Verifier(k=config['k'], m=config['m'], mode="liar")
            liar_res = evaluate_liar(verifier, args.samples)
            row["liar_f1"] = liar_res['f1']
            
        all_results.append(row)
        
    print("\n--- ABLATION STUDY TABLE ---")
    df = pd.DataFrame(all_results)
    print(df.to_markdown(index=False))
    
    print("\nEvaluation Complete.")

if __name__ == "__main__":
    main()
