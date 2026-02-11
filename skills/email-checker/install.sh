#!/bin/bash
# Install Email Checker Skill for OpenClaw

SKILL_NAME="email-checker"
SKILL_DIR="/home/zhangcb/.openclaw/skills/$SKILL_NAME"
SOURCE_DIR="/home/zhangcb/.openclaw/workspace/email-checker"

echo "Installing Email Checker Skill..."

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
    echo "✅ Email Checker Skill installed successfully!"
    echo "Files copied to: $SKILL_DIR"
    echo ""
    echo "Next steps:"
    echo "1. Skill registered in OpenClaw"
    echo "2. Ready to use email checking functions"
    echo ""
    echo "The skill will:"
    echo "- Check for new emails regularly"
    echo "- Send notifications when new emails arrive"
    echo "- Maintain email history to avoid duplicates"
    echo ""
    echo "To schedule automatic checks, use OpenClaw's cron functionality:"
    echo "openclaw cron add --name 'Email Check' --cron '*/30 * * * *' --system-event 'Check emails' --session main"
else
    echo "❌ Installation failed!"
fi