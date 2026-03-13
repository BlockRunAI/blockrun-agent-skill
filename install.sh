#!/bin/bash
# BlockRun Install Script
# One command to install BlockRun skill + SDK
#
# Usage:
#   bash install.sh              # Default: Base chain (USDC on Base)
#   CHAIN=solana bash install.sh # Solana chain (USDC on Solana)

set -e

# Chain selection (default: base)
CHAIN="${CHAIN:-base}"
echo "Installing BlockRun (chain: $CHAIN)..."

# Detect platform and set skills path
if [ -d "$HOME/.gemini/antigravity" ]; then
    SKILLS_DIR="$HOME/.gemini/antigravity/skills/blockrun"
    echo "Detected Antigravity (global)"
elif [ -d "$HOME/.claude" ]; then
    SKILLS_DIR="$HOME/.claude/skills/blockrun"
    echo "Detected Claude Code"
else
    # Default to Claude Code
    SKILLS_DIR="$HOME/.claude/skills/blockrun"
    mkdir -p "$HOME/.claude/skills"
    echo "Using Claude Code default"
fi

# Clone or update skill
if [ ! -d "$SKILLS_DIR" ]; then
    echo "Cloning skill..."
    mkdir -p "$(dirname "$SKILLS_DIR")"
    git clone --depth 1 --quiet https://github.com/BlockRunAI/blockrun-agent-wallet "$SKILLS_DIR"
else
    echo "Updating skill..."
    cd "$SKILLS_DIR" && git pull --ff-only --quiet
fi

# Install SDK with fallbacks for different Python setups
if [ "$CHAIN" = "solana" ]; then
    PKG="blockrun-llm[solana]"
else
    PKG="blockrun-llm"
fi
echo "Installing Python SDK ($PKG)..."
if pip install --upgrade "$PKG" >/dev/null 2>&1; then
    :
elif pip install --user --upgrade "$PKG" >/dev/null 2>&1; then
    :
elif pip install --user --break-system-packages --upgrade "$PKG" >/dev/null 2>&1; then
    :
elif python3 -m pip install --upgrade "$PKG" >/dev/null 2>&1; then
    :
elif python3 -m pip install --user --upgrade "$PKG" >/dev/null 2>&1; then
    :
elif python3 -m pip install --user --break-system-packages --upgrade "$PKG" >/dev/null 2>&1; then
    :
else
    echo "ERROR: Could not install $PKG. Please install manually:"
    echo "  pip install $PKG"
    exit 1
fi

# Install CLI to ~/.local/bin
echo "Installing CLI..."
mkdir -p "$HOME/.local/bin"
cp "$SKILLS_DIR/bin/blockrun" "$HOME/.local/bin/blockrun"
chmod +x "$HOME/.local/bin/blockrun"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    echo "Adding ~/.local/bin to PATH..."
    # Add to shell config
    if [ -f "$HOME/.zshrc" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
    elif [ -f "$HOME/.bashrc" ]; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
    # Also export for current session
    export PATH="$HOME/.local/bin:$PATH"
fi

# Save chain preference
mkdir -p "$HOME/.blockrun"
echo "$CHAIN" > "$HOME/.blockrun/.chain"

# Verify installation and show status
echo "Verifying..."
python3 - "$CHAIN" <<'PYEOF'
import sys
chain = sys.argv[1] if len(sys.argv) > 1 else "base"

if chain == "solana":
    from blockrun_llm import setup_agent_solana_wallet
    from blockrun_llm.solana_wallet import save_solana_wallet_qr
    client = setup_agent_solana_wallet(silent=True)
    addr = client.get_wallet_address()
    from blockrun_llm import get_solana_usdc_balance
    balance = get_solana_usdc_balance(addr)
    save_solana_wallet_qr(addr)
    qr_file = "solana_qr.png"
    chain_label = "Solana"
    fund_msg = "Fund wallet: Send USDC on Solana to the address above"
else:
    from blockrun_llm import setup_agent_wallet, save_wallet_qr
    client = setup_agent_wallet(silent=True)
    addr = client.get_wallet_address()
    balance = client.get_balance()
    save_wallet_qr(addr)
    qr_file = "qr.png"
    chain_label = "Base"
    fund_msg = "Fund wallet: Send USDC on Base to the address above"

print()
print(f'BlockRun installed! (Chain: {chain_label})')
print(f'Wallet: {addr}')
print(f'Balance: ${balance:.2f} USDC')
print()
print('Your agent can now:')
print('  Generate images      - "generate a logo for my startup"')
print('  Access X/Twitter     - "get followers of @blockrunai"')
print('  Edit images          - "edit this image to make the sky purple"')
print('  Search the web       - "search latest AI news"')
print('  Get second opinions  - "GPT review this code"')
print()
print('Just ask Claude naturally. No "blockrun" prefix needed.')
if balance == 0:
    print()
    print(fund_msg)
print()
print(f'To switch chains: echo "solana" > ~/.blockrun/.chain  (or "base")')
sys.stdout.flush()
PYEOF

# Delay so user can read output before QR opens
sleep 3

# Open QR code AFTER all text is printed
for qr in "$HOME/.blockrun/qr.png" "$HOME/.blockrun/solana_qr.png"; do
    if [ -f "$qr" ]; then
        open "$qr" 2>/dev/null || xdg-open "$qr" 2>/dev/null || true
        break
    fi
done
