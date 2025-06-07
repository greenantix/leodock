import requests
import json

def ask_archie_for_embeddings(text):
    response = requests.post("http://127.0.0.1:1234/v1/embeddings",
        json={
            "model": "text-embedding-nomic-embed-text-v1.5-embedding", 
            "input": text
        })
    
    if response.status_code == 200:
        embedding = response.json()['data'][0]['embedding']
        return f"Archie generated embedding vector of length {len(embedding)} for your text"
    else:
        return f"Error talking to Archie: {response.status_code}"

# Example usage  
if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
        result = ask_archie_for_embeddings(text)
        print(f"Archie says: {result}")
    else:
        print("Usage: python talk_to_archie.py <text to embed>")