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

# Install SDK from PyPI (--no-cache-dir ensures latest version)
if [ "$CHAIN" = "solana" ]; then
    PKG="blockrun-llm[solana]>=0.7.4"
else
    PKG="blockrun-llm>=0.7.4"
fi
echo "Installing Python SDK ($PKG) from PyPI..."
INSTALLED=false
for cmd in \
    "python3 -m pip install --no-cache-dir --upgrade \"$PKG\"" \
    "pip install --no-cache-dir --upgrade \"$PKG\"" \
    "python3 -m pip install --no-cache-dir --user --upgrade \"$PKG\"" \
    "python3 -m pip install --no-cache-dir --break-system-packages --upgrade \"$PKG\""; do
    if eval "$cmd" 2>&1 | tail -1; then
        INSTALLED=true
        break
    fi
done

if [ "$INSTALLED" = false ]; then
    echo "ERROR: Could not install $PKG"
    echo "Run manually: pip install --no-cache-dir \"$PKG\""
    exit 1
fi

# Save chain preference
mkdir -p "$HOME/.blockrun"
echo "$CHAIN" > "$HOME/.blockrun/.chain"

# Verify the package is importable
if python3 -c "import blockrun_llm; print(f'SDK v{blockrun_llm.__version__} installed')" 2>/dev/null; then
    # Run full verification
    python3 - "$CHAIN" <<'PYEOF'
import sys
chain = sys.argv[1] if len(sys.argv) > 1 else "base"

if chain == "solana":
    try:
        from blockrun_llm import setup_agent_solana_wallet
        client = setup_agent_solana_wallet(silent=True)
        addr = client.get_wallet_address()
        balance = client.get_balance()
        chain_label = "Solana"
        fund_msg = "Fund wallet: Send USDC on Solana to the address above"
    except ImportError as e:
        import blockrun_llm
        v = getattr(blockrun_llm, '__version__', 'unknown')
        print(f'\nERROR: Solana extras missing (installed: v{v})')
        print(f'Import error: {e}')
        print('Fix: pip install --no-cache-dir "blockrun-llm[solana]>=0.7.4"')
        sys.exit(1)
else:
    from blockrun_llm import setup_agent_wallet
    client = setup_agent_wallet(silent=True)
    addr = client.get_wallet_address()
    balance = client.get_balance()
    chain_label = "Base"
    fund_msg = "Fund wallet: Send USDC on Base to the address above"

print()
print(f'BlockRun installed! (Chain: {chain_label})')
print(f'Wallet: {addr}')
print(f'Balance: ${balance:.2f} USDC')
if balance == 0:
    print()
    print(fund_msg)
print()
print('Try: "What\'s trending on X?" or "Generate a logo for my project"')
sys.stdout.flush()
PYEOF
else
    # Package installed to a different python than python3 — tell user how to fix
    echo ""
    echo "BlockRun skill cloned and chain preference saved."
    echo ""
    echo "NOTE: blockrun-llm was installed but your current python3 can't find it."
    echo "This usually means you're using a virtual environment."
    echo "Run this in your active environment:"
    echo ""
    echo "  pip install --no-cache-dir \"$PKG\""
    echo ""
fi
