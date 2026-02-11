#!/bin/bash
# Install TTG Scraper Skill for OpenClaw

SKILL_NAME="ttg-scraper"
SKILL_DIR="/home/zhangcb/.openclaw/skills/$SKILL_NAME"
SOURCE_DIR="/home/zhangcb/.openclaw/workspace/ttg-scraper"

echo "Installing TTG Scraper Skill..."

# Create skills directory if it doesn't exist
mkdir -p /home/zhangcb/.openclaw/skills

# Remove existing skill if it exists
if [ -d "$SKILL_DIR" ]; then
    echo "Removing existing $SKILL_NAME skill..."
    rm -rf "$SKILL_DIR"
fi

# Copy skill files
echo "Copying skill files..."
cp -r "$SOURCE_DIR" "$SKILL_DIR"

# Install dependencies
echo "Installing dependencies..."
source /home/zhangcb/.nvm/nvm.sh
pip3 install --break-system-packages requests beautifulsoup4 schedule

# Verify the installation
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "✅ TTG Scraper Skill installed successfully!"
    echo "Files copied to: $SKILL_DIR"
    echo ""
    echo "Next steps:"
    echo "1. Dependencies installed: requests, beautifulsoup4, schedule"
    echo "2. Skill registered in OpenClaw"
    echo "3. Ready to use monitoring functions"
    echo ""
    echo "To start the monitoring service:"
    echo "cd /home/zhangcb/.openclaw/workspace/ttg-scraper"
    echo "python3 ttg_monitor.py"
    echo ""
    echo "The service will automatically check for new content at:"
    echo "- 08:00 (morning)"
    echo "- 13:00 (afternoon)" 
    echo "- 19:00 (evening)"
    echo "every day, and notify you via DingTalk and WhatsApp if new movies are found."
else
    echo "❌ Installation failed!"
fi