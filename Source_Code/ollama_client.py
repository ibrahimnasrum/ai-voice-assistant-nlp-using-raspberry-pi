import requests

def ollama_generate(prompt: str, model: str = "llama3:latest", host: str = "http://localhost:11434") -> str:
    """
    Simple text generation via Ollama local REST API.
    Ollama is already running in your machine (port 11434).
    """
    url = f"{host}/api/generate"
    payload = {
        "model": model,          # e.g. "llama3:latest" or "qwen2.5:7b"
        "prompt": prompt,
        "stream": False
    }

    try:
        r = requests.post(url, json=payload, timeout=60)
        r.raise_for_status()
        return (r.json().get("response") or "").strip()
    except requests.exceptions.RequestException as e:
        return f"Maaf, saya tak dapat hubungi Ollama di {host}. Error: {e}"
