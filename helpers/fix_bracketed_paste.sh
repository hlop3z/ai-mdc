#!/bin/bash

# Ensure .inputrc exists and has the correct setting
INPUTRC_FILE="$HOME/.inputrc"
BASHRC_FILE="$HOME/.bashrc"
BIND_LINE="set enable-bracketed-paste off"

echo "Updating $INPUTRC_FILE..."
if ! grep -Fxq "$BIND_LINE" "$INPUTRC_FILE" 2>/dev/null; then
    echo "$BIND_LINE" >>"$INPUTRC_FILE"
    echo "✓ Added to .inputrc"
else
    echo "✓ .inputrc already configured"
fi

# Ensure .bashrc contains bind command for immediate shell usage
echo "Updating $BASHRC_FILE..."
BASHRC_BIND_LINE="bind 'set enable-bracketed-paste off'"
if ! grep -Fxq "$BASHRC_BIND_LINE" "$BASHRC_FILE" 2>/dev/null; then
    echo "$BASHRC_BIND_LINE" >>"$BASHRC_FILE"
    echo "✓ Added to .bashrc"
else
    echo "✓ .bashrc already configured"
fi

# Apply changes immediately
echo "Applying settings..."
bind -f "$INPUTRC_FILE"
eval "$BASHRC_BIND_LINE"

echo "✅ Bracketed paste should now be disabled in Git Bash."
