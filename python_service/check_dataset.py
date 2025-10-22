import json
import os

DATASET_PATH = os.path.join(os.path.dirname(__file__), "trig_dataset.json")

try:
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    print("✅ JSON loaded successfully!")
    print(f"📊 Data type: {type(data)}")
    print(f"📊 Data length: {len(data)}")
    print(f"📊 Dictionary keys: {list(data.keys())}")
    
    # Check what's under the first key
    first_key = list(data.keys())[0]
    print(f"📊 First key '{first_key}' contains: {type(data[first_key])}")
    print(f"📊 Sample of first key content: {data[first_key]}")
    
except Exception as e:
    print(f"❌ Error loading dataset: {e}")