
import logging
from agents.model import get_model

# Enable logging
logging.basicConfig(level=logging.INFO)

print("🔍 Testing Rate Limiter...")
model = get_model()

print(f"📦 Model Class: {type(model)}")
print(f"📦 Model ID: {model.id}")

# Test 1: Calling response()
print("\n[Test 1] Calling model.response()...")
try:
    resp = model.response("Hello")
    print("✅ Response returned.")
except Exception as e:
    print(f"❌ Response failed: {e}")

# Check what other methods exist
print("\n[Info] Methods on model object:")
for attr in dir(model):
    if not attr.startswith("_") and callable(getattr(model, attr)):
        print(f" - {attr}")
