#!/usr/bin/env python3
"""
Train a simple sentiment model and export to ONNX
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import pickle
import os

try:
    from skl2onnx import convert_sklearn
    from skl2onnx.common.data_types import StringTensorType
    HAS_SKL2ONNX = True
except ImportError:
    HAS_SKL2ONNX = False
    print("⚠️ skl2onnx not installed. Run: pip install skl2onnx")

def train_model():
    """Train a simple sentiment model"""
    print("📝 Training sentiment model...")
    
    # Sample training data (positive/negative)
    texts = [
        "This cat is adorable", "I love this", "Amazing!", "Great work", "So happy",
        "Wonderful day", "Cute cat", "Beautiful", "Fantastic", "Best ever",
        "I hate this", "Terrible", "Worst ever", "Bad experience", "Horrible",
        "Awful", "Disappointing", "Not good", "Useless", "Waste of time"
    ]
    labels = [1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0]
    
    # Create and train pipeline
    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(max_features=200)),
        ('clf', LogisticRegression())
    ])
    pipeline.fit(texts, labels)
    
    # Save as pickle
    with open("sentiment_pipeline.pkl", "wb") as f:
        pickle.dump(pipeline, f)
    print("✅ Saved sentiment_pipeline.pkl")
    
    # Convert to ONNX if available
    if HAS_SKL2ONNX:
        try:
            initial_type = [('input', StringTensorType([None, 1]))]
            onnx_model = convert_sklearn(pipeline, initial_types=initial_type)
            with open("sentiment_model.onnx", "wb") as f:
                f.write(onnx_model.SerializeToString())
            print("✅ Saved sentiment_model.onnx")
            size = os.path.getsize("sentiment_model.onnx") / 1024
            print(f"   Size: {size:.1f} KB")
        except Exception as e:
            print(f"⚠️ ONNX export failed: {e}")
            print("   Will use pickle model instead")
    else:
        print("⚠️ skl2onnx not installed. Run: pip install skl2onnx")
        print("   Will use pickle model instead")
    
    return pipeline

if __name__ == "__main__":
    # Install skl2onnx if needed
    if not HAS_SKL2ONNX:
        print("Installing skl2onnx...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "skl2onnx"])
        print("Please rerun the script")
    else:
        train_model()
