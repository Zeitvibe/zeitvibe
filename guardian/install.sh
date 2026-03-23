#!/bin/bash
# ZeitVibe Guardian Installer

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     ZEITVIBE GUARDIAN INSTALLER                          ║"
echo "╚══════════════════════════════════════════════════════════╝"

cd ~
mkdir -p projects
cd projects

# Clone if not exists
if [ ! -d "zeitvibe" ]; then
    git clone https://github.com/Zeitvibe/zeitvibe.git
fi

cd zeitvibe/guardian
./install_hook.sh

echo "✅ Guardian installed! Run 'source ~/.zshrc' to activate."
