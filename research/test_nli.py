from transformers import pipeline

model_name = 'facebook/bart-large-mnli'
nli_pipeline = pipeline("text-classification", model=model_name, device=-1)

evidence = "The Sun is a star."
claim = "The Sun is a star."

print("Testing direct call with f-string...")
try:
    res = nli_pipeline(f"{evidence} {claim}")
    print(f"Result 1: {res}")
except Exception as e:
    print(f"Error 1: {e}")

print("\nTesting dict call...")
try:
    res = nli_pipeline({"text": evidence, "text_pair": claim})
    print(f"Result 2: {res}")
except Exception as e:
    print(f"Error 2: {e}")

print("\nTesting positional pair call...")
try:
    # Some older versions or specific models use this
    res = nli_pipeline(evidence, claim)
    print(f"Result 3: {res}")
except Exception as e:
    print(f"Error 3: {e}")
print("\nTesting tuple call...")
try:
    res = nli_pipeline((evidence, claim))
    print(f"Result 4: {res}")
except Exception as e:
    print(f"Error 4: {e}")

print("\nTesting list of tuples call...")
try:
    res = nli_pipeline([(evidence, claim)])
    print(f"Result 5: {res}")
except Exception as e:
    print(f"Error 5: {e}")
