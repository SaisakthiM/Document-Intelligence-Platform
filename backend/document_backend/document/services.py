import requests
import os
import uuid
from dotenv import load_dotenv
from google import genai
from minio import Minio
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer("all-MiniLM-L6-v2")

load_dotenv()

PORT = os.getenv("PORT_AI", "11434")
OLLAMA_URL = f"http://localhost:{PORT}/api/generate"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MINIO_SECURE = os.getenv("MINIO_SECURE")

client = genai.Client(api_key=GEMINI_API_KEY)
client_minio = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)

def get_embedding(text):
    return model.encode(text)

def summarize_ollama(prompt: str, model: str = "phi3"):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
        return data.get("response")
    except requests.exceptions.RequestException as e:
        print(f"[OLLAMA ERROR]: {e}")
        return None

def summarize_gemini(prompt: str, model: str = "gemini-3-flash-preview"):
    try:
        response = client.models.generate_content(
            model=model,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"[GEMINI ERROR]: {e}")
        return None


def generate_summary(prompt: str, model_choice: str = "ollama") -> str or None:

    model_choice = model_choice.lower()

    if model_choice == "ollama":
        result = summarize_ollama(prompt)
        if result:
            return result.strip(), "ollama"

        # fallback
        result = summarize_gemini(prompt)
        if result:
            return result.strip(), "gemini_fallback"

        return None, "failed"

    elif model_choice == "gemini":
        result = summarize_gemini(prompt)
        if result:
            return result.strip(), "gemini"

        # fallback
        result = summarize_ollama(prompt)
        if result:
            return result.strip(), "ollama_fallback"

        return None, "failed"

    return None, "invalid_model"

def get_recommendations(target_book, all_books, top_k=3):
    target_text = f"{target_book.title} {target_book.description}"
    target_embedding = get_embedding(target_text)

    results = []

    for book in all_books:
        if book.id == target_book.id:
            continue

        text = f"{book.title} {book.description}"
        emb = get_embedding(text)

        score = cosine_similarity([target_embedding], [emb])[0][0]

        results.append((book, score))

    # sort by similarity
    results.sort(key=lambda x: x[1], reverse=True)

    # return top K books
    return [book for book, _ in results[:top_k]]

def upload_to_minio(file, filename=None):
    bucket = MINIO_BUCKET

    if not client_minio.bucket_exists(bucket):
        client_minio.make_bucket(bucket)

    ext = os.path.splitext(file.name)[1]
    object_name = filename or f"{uuid.uuid4()}{ext}"

    client_minio.put_object(
        bucket,
        object_name,
        file,
        length=file.size,
        content_type=file.content_type,
    )

    return f"http://{MINIO_ENDPOINT}/{bucket}/{object_name}"
