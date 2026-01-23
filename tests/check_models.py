import google.genai as genai
import os
from dotenv import load_dotenv

# Load your .env file
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not api_key:
    print("[X] Error: No API key found in .env (GEMINI_API_KEY or GOOGLE_API_KEY)")
else:
    try:
        client = genai.Client(api_key=api_key)
        print(f"[OK] API Key found: {api_key[:5]}...")
        print("\n[INFO] Fetching available models for you...")
        
        found_any = False
        # New API: client.models.list()
        for m in client.models.list():
            # Check if model supports generation
            if hasattr(m, 'supported_generation_methods') and 'generateContent' in m.supported_generation_methods:
                # Strip 'models/' prefix for easier reading
                model_id = m.name.replace("models/", "") if hasattr(m, 'name') else str(m)
                print(f" - {model_id}")
                found_any = True
        
        if not found_any:
            print("[!] No models found. Your API key might be invalid or has no credits.")
            
    except Exception as e:
        print(f"[X] Connection failed: {e}")