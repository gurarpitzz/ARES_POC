from verifier import Verifier
import pandas as pd
from tabulate import tabulate

def main():
    # Sample claims representative of the datasets
    # Claim type: (True/False/Uncertain)
    test_claims = [
        ("The Earth orbits the Sun", "VERIFIED"),
        ("The moon is made of green cheese", "MISINFORMATION"),
        ("Narendra Modi is the Prime Minister of India", "VERIFIED"),
        ("The population of Mars is 1 billion", "MISINFORMATION"),
        ("Artificial Intelligence will replace all humans", "UNCERTAIN")
    ]
    
    configs = [
        {"k": 3, "theta": 0.5},
        {"k": 5, "theta": 0.6},
        {"k": 10, "theta": 0.7}
    ]
    
    all_results = []
    
    for config in configs:
        print(f"\n>>> Evaluating configuration: k={config['k']}, theta={config['theta']}")
        verifier = Verifier(k=config['k'], theta=config['theta'])
        
        correct = 0
        total = len(test_claims)
        
        for claim, ground_truth in test_claims:
            print(f"Testing: {claim[:30]}...")
            try:
                res = verifier.verify(claim)
                if res['verdict'] == ground_truth:
                    correct += 1
                print(f"  Result: {res['verdict']} | GT: {ground_truth}")
            except Exception as e:
                print(f"  Error: {e}")
        
        accuracy = correct / total
        all_results.append({
            "k": config['k'],
            "theta": config['theta'],
            "accuracy": accuracy
        })
        
    print("\n--- ARES_POC MANUAL ABLATION TABLE ---")
    df = pd.DataFrame(all_results)
    print(df.to_markdown(index=False))

if __name__ == "__main__":
    main()
