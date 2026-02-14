from sentence_transformers import SentenceTransformer
try:
    print("Starting download...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model downloaded successfully")
except Exception as e:
    print(f"Error: {e}")
