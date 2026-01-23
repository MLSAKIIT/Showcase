
import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Get Gemini model
try:
    from agno.models.google import Gemini
except ImportError:
    print("Error: agno not installed. Run 'pip install agno'")
    sys.exit(1)

# API Key Validation Logic (Same as in our agents)
_api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

if not _api_key:
    print("❌ No API key found! Set GEMINI_API_KEY or GOOGLE_API_KEY in .env")
    sys.exit(1)

print(f"Found API Key: {_api_key[:5]}...{_api_key[-5:]}")

# Initialize Model
try:
    model = Gemini(id="gemini-2.0-flash", api_key=_api_key)
    print("Initialized Gemini model...")
except Exception as e:
    print(f"Failed to initialize model: {e}")
    sys.exit(1)

# Test Generation
print("Sending test request to Google Gemini...")
try:
    response = model.response("Say 'API Key is working!' if you can read this.")
    print("\nSUCCESS! Response:")
    print("-" * 20)
    print(response.content)
    print("-" * 20)
except Exception as e:
    print(f"\nAPI Key Error: {e}")
    print("Please check if your key is valid and has access to Gemini 2.0 Flash.")
