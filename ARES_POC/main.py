import argparse
from verifier import Verifier
import json

def main():
    parser = argparse.ArgumentParser(description="ARES_POC: Research-Grade Verification Engine")
    parser.add_argument("claim", type=str, help="The claim to verify")
    parser.add_argument("--k", type=int, default=10, help="Retrieval depth (R operator)")
    parser.add_argument("--m", type=int, default=5, help="Top-M selection (S operator)")
    
    args = parser.parse_args()
    
    print(f"\n--- ARES_POC VERIFICATION ---")
    print(f"Claim: {args.claim}")
    print(f"Parameters: k={args.k}, m={args.m}")
    print(f"------------------------------\n")
    
    verifier = Verifier(k=args.k, m=args.m)
    result = verifier.verify(args.claim)
    
    print(json.dumps(result, indent=2))
    
    print(f"\nFINAL VERDICT: {result['verdict']}")
    print(f"TRUTH SCORE: {result['truth_score']:.4f}")
    print(f"CONFIDENCE: {result['confidence']:.4f}")

if __name__ == "__main__":
    main()
