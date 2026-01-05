from router import get_response

def main():
    print("=== TEST TEXT MODE (tanpa suara) ===")
    print("Taip soalan. Contoh: Asar Gombak")
    print("Taip 'exit' untuk keluar.\n")

    while True:
        q = input("You: ").strip()
        if q.lower() in ("exit", "quit"):
            break
        ans = get_response(q, ollama_model="llama3:latest")
        print("Bot:", ans, "\n")

if __name__ == "__main__":
    main()
