#!/bin/bash
# ZeitVibe Sentiment Installer

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     ZEITVIBE SENTIMENT INSTALLER                         ║"
echo "╚══════════════════════════════════════════════════════════╝"

cd ~/projects/zeitvibe/sentiment

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install onnxruntime emoji

echo "✅ Sentiment installed!"
echo "Run: cd ~/projects/zeitvibe/sentiment && source venv/bin/activate && python3 emoji_sentiment.py"
