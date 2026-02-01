from datasets import load_dataset_builder
try:
    builder = load_dataset_builder("liar")
    print(f"Liar builder path: {builder.code_path}")
except Exception as e:
    print(f"Error: {e}")

try:
    builder = load_dataset_builder("ucsbnlp/liar")
    print(f"UCSB Liar builder path: {builder.code_path}")
except Exception as e:
    print(f"Error: {e}")
