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

# Install SDK — use python3 -m pip (works in venvs and system python)
if [ "$CHAIN" = "solana" ]; then
    PKG="blockrun-llm[solana]>=0.7.2"
else
    PKG="blockrun-llm>=0.7.2"
fi
echo "Installing Python SDK ($PKG)..."
if python3 -m pip install --upgrade "$PKG" 2>&1 | tail -1; then
    :
elif python3 -m pip install --user --upgrade "$PKG" 2>&1 | tail -1; then
    :
elif pip install --upgrade "$PKG" 2>&1 | tail -1; then
    :
elif python3 -m pip install --break-system-packages --upgrade "$PKG" 2>&1 | tail -1; then
    :
else
    echo "ERROR: Could not install $PKG. Please install manually:"
    echo "  pip install \"$PKG\""
    exit 1
fi

# Verify the package is importable by the SAME python3
if ! python3 -c "import blockrun_llm" 2>/dev/null; then
    echo "WARNING: blockrun-llm installed but not importable by python3."
    echo "If you're using a virtual environment, activate it and run:"
    echo "  pip install \"$PKG\""
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
    try:
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
    except ImportError as e:
        import blockrun_llm
        v = getattr(blockrun_llm, '__version__', 'unknown')
        print(f'\nERROR: Solana wallet requires blockrun-llm >= 0.7.0 (installed: {v})')
        print(f'Import error: {e}')
        print('Fix: pip install --upgrade --no-cache-dir "blockrun-llm[solana]>=0.7.2"')
        sys.exit(1)
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

# QR codes saved to ~/.blockrun/ — user can open manually if needed
