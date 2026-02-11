#!/bin/bash
# Install System Update Manager Skill for OpenClaw

SKILL_NAME="sys-updater"
SKILL_DIR="/home/zhangcb/.openclaw/skills/$SKILL_NAME"
SOURCE_DIR="/home/zhangcb/.openclaw/workspace/sys-updater"

echo "Installing System Update Manager Skill..."

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
    echo "✅ System Update Manager Skill installed successfully!"
    echo "Files copied to: $SKILL_DIR"
    echo ""
    echo "Next steps:"
    echo "1. Skill registered in OpenClaw"
    echo "2. Ready to use system update management functions"
    echo ""
    echo "The skill will:"
    echo "- Check for system updates regularly"
    echo "- Send notifications when updates are available"
    echo "- Maintain update history"
    echo ""
    echo "To schedule automatic checks, use OpenClaw's cron functionality:"
    echo "openclaw cron add --name 'Weekly System Update Check' --cron '0 9 * * 1' --system-event 'Check system updates' --session main"
else
    echo "❌ Installation failed!"
fi