#!/bin/bash
# Install AMap Skill for OpenClaw

SKILL_NAME="amap"
SKILL_DIR="/home/zhangcb/.openclaw/skills/$SKILL_NAME"
SOURCE_DIR="/home/zhangcb/.openclaw/workspace/amap-skill"

echo "Installing AMap Skill..."

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

# Verify the installation
if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo "✅ AMap Skill installed successfully!"
    echo "Files copied to: $SKILL_DIR"
    echo ""
    echo "Next steps:"
    echo "1. Get an API key from https://lbs.amap.com/"
    echo "2. Set the environment variable:"
    echo "   export AMAP_API_KEY='your_api_key_here'"
    echo "3. Restart OpenClaw gateway for the skill to be recognized"
    echo ""
    echo "To restart OpenClaw gateway:"
    echo "source /etc/profile && source /home/zhangcb/.nvm/nvm.sh && cd /home/zhangcb/.nvm/versions/node/v24.13.0/lib/node_modules/openclaw && npm start -- gateway restart"
else
    echo "❌ Installation failed!"
fi