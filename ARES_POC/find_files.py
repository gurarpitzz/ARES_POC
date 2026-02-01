from huggingface_hub import list_repo_files
try:
    files = list_repo_files("ucsbnlp/liar", repo_type="dataset")
    print(f"LIAR files: {files}")
except Exception as e:
    print(f"LIAR error: {e}")

try:
    files = list_repo_files("fever", repo_type="dataset")
    print(f"FEVER files: {files}")
except Exception as e:
    print(f"FEVER error: {e}")
