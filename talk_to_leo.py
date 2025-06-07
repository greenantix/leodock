import requests
import json
from leo_config import LEO_SYSTEM_PROMPT, LEO_SETTINGS

def talk_to_leo(message, mode="general", context=""):
    """Enhanced Leo communication with personality"""
    
    if mode == "code_analysis":
        system_prompt = LEO_SYSTEM_PROMPT + "\n\nCURRENT MODE: Code Analysis - Be direct and actionable."
    elif mode == "debugging":
        system_prompt = LEO_SYSTEM_PROMPT + "\n\nCURRENT MODE: Debugging - Be methodical and encouraging."
    else:
        system_prompt = LEO_SYSTEM_PROMPT
    
    response = requests.post("http://127.0.0.1:1234/v1/chat/completions", 
        json={
            "model": "meta-llama-3.1-8b-instruct",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context: {context}\n\nClaude Code: {message}"}
            ],
            **LEO_SETTINGS
        })
    
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content']
    else:
        return f"Leo connection error: {response.status_code}"

# Usage examples:
# talk_to_leo("How should I structure this new feature?", mode="code_analysis")
# talk_to_leo("I'm getting a weird error in the terminal", mode="debugging")