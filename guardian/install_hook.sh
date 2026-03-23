#!/bin/bash
# Install ZeitVibe Command Guardian Zsh Hook

GUARDIAN_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "🔧 Installing ZeitVibe Command Guardian..."

# Check if already installed
if grep -q "ZeitVibe Command Guardian" ~/.zshrc; then
    echo "✅ Already installed. Skipping..."
    exit 0
fi

# Add to .zshrc
cat >> ~/.zshrc << 'ZSH_EOF'

# ============================================
# ZeitVibe Command Guardian
# ============================================
preexec() {
    # Log command before execution
    python3 $GUARDIAN_DIR/command_logger.py "$1"
}
ZSH_EOF

echo "✅ Added to .zshrc"
echo ""
echo "📝 To activate: source ~/.zshrc"
echo "   Or restart your terminal"
