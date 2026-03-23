import onnxruntime as ort
import numpy as np
import emoji
import re

def extract_emojis(text):
    """Extract emojis from text"""
    return ''.join(c for c in text if c in emoji.EMOJI_DATA)

print("🚀 Loading sentiment model...")
session = ort.InferenceSession("sentiment_model.onnx")
input_name = session.get_inputs()[0].name

# Sample cat comments (replace with real data later)
comments = [
    "This cat is so cute! 😍😍😍",
    "I hate cats 😡",
    "Look at this fluffy kitty 😂",
    "My cat passed away 😢😢😢",
    "Interesting cat behavior 🤔",
    "Best cat ever! ❤️🐱",
    "Why does my cat do this? 😾",
    "Cuteness overload! 😻",
]

print("\n📊 Cat Comment Sentiment Analysis")
print("=" * 50)

# Counters for emoji chart
emojis_count = {}

for comment in comments:
    # Get sentiment
    input_data = np.array([[comment]]).astype(np.object_)
    result = session.run(None, {input_name: input_data})
    label = result[0][0]
    
    # Extract emojis
    found_emojis = extract_emojis(comment)
    for e in found_emojis:
        emojis_count[e] = emojis_count.get(e, 0) + 1
    
    # Show result
    sentiment = "😊" if label == 1 else "😞"
    print(f"{sentiment} {comment[:50]}")
    if found_emojis:
        print(f"   Emojis: {found_emojis}")

print("\n" + "=" * 50)
print("📊 EMOJI MOOD MATRIX")
print("=" * 50)

# Show emoji bar chart
total = sum(emojis_count.values())
for emoji_char, count in sorted(emojis_count.items(), key=lambda x: x[1], reverse=True):
    percent = int(count / total * 50)
    bar = emoji_char * percent
    print(f"{emoji_char} {bar} {count} ({percent/2:.0f}%)")

print("\n✅ Analysis complete!")
