#!/bin/bash
# SocialClaw Install Script
# One command to install SocialClaw skill + SDK
#
# Usage:
#   bash install.sh              # Default: Base chain (USDC on Base)
#   CHAIN=solana bash install.sh # Solana chain (USDC on Solana)

set -e

# Chain selection (default: base)
CHAIN="${CHAIN:-base}"
echo "Installing SocialClaw (chain: $CHAIN)..."

# ── Python detection ──────────────────────────────────────────────
# Priority: active venv → python3 on PATH → python on PATH
PYTHON=""

if [ -n "$VIRTUAL_ENV" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
    PYTHON="$VIRTUAL_ENV/bin/python"
elif command -v python3 >/dev/null 2>&1; then
    PYTHON="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON="python"
fi

if [ -z "$PYTHON" ]; then
    echo "ERROR: No Python interpreter found."
    echo "Install Python 3.8+ and try again."
    exit 1
fi

# Verify Python >= 3.8
PY_OK=$("$PYTHON" -c "import sys; print(int(sys.version_info >= (3, 8)))" 2>/dev/null || echo "0")
if [ "$PY_OK" != "1" ]; then
    PY_VER=$("$PYTHON" --version 2>&1 || echo "unknown")
    echo "ERROR: Python 3.8+ required (found: $PY_VER)"
    exit 1
fi

echo "Using Python: $("$PYTHON" --version 2>&1) ($PYTHON)"

# ── Detect platform and set skills path ───────────────────────────
# Install to ALL detected platforms so both Claude Code and Antigravity work
SKILLS_DIRS=()

if [ -d "$HOME/.claude" ]; then
    SKILLS_DIRS+=("$HOME/.claude/skills/socialclaw")
fi

if [ -d "$HOME/.gemini/antigravity" ]; then
    SKILLS_DIRS+=("$HOME/.gemini/antigravity/skills/socialclaw")
fi

# If neither detected, default to Claude Code
if [ ${#SKILLS_DIRS[@]} -eq 0 ]; then
    mkdir -p "$HOME/.claude/skills"
    SKILLS_DIRS+=("$HOME/.claude/skills/socialclaw")
fi

# Clone or update skill in each target
FIRST_DIR=""
for SKILLS_DIR in "${SKILLS_DIRS[@]}"; do
    PLATFORM=$(echo "$SKILLS_DIR" | grep -q ".gemini" && echo "Antigravity" || echo "Claude Code")

    if [ -z "$FIRST_DIR" ]; then
        # First target: clone or update normally
        if [ ! -d "$SKILLS_DIR" ]; then
            echo "Installing skill ($PLATFORM)..."
            mkdir -p "$(dirname "$SKILLS_DIR")"
            git clone --depth 1 --quiet https://github.com/BlockRunAI/socialclaw "$SKILLS_DIR"
        else
            echo "Updating skill ($PLATFORM)..."
            cd "$SKILLS_DIR" && git pull --ff-only --quiet
        fi
        FIRST_DIR="$SKILLS_DIR"
    else
        # Additional targets: symlink to first to avoid duplicate clones
        if [ ! -e "$SKILLS_DIR" ]; then
            echo "Linking skill ($PLATFORM)..."
            mkdir -p "$(dirname "$SKILLS_DIR")"
            ln -sf "$FIRST_DIR" "$SKILLS_DIR"
        else
            echo "Skill already present ($PLATFORM)"
        fi
    fi
done

# ── Install SDK from PyPI (quiet, verbose only on failure) ────────
if [ "$CHAIN" = "solana" ]; then
    PKG="blockrun-llm[solana]>=0.8.0"
else
    PKG="blockrun-llm>=0.8.0"
fi
echo "Installing Python SDK..."

INSTALLED=false
PIP_LOG=$(mktemp)

# Strategy 1: default pip install
if "$PYTHON" -m pip install -q --no-cache-dir --upgrade "$PKG" > "$PIP_LOG" 2>&1; then
    INSTALLED=true
fi

# Strategy 2: --user flag (no write access to site-packages)
if [ "$INSTALLED" = false ]; then
    if "$PYTHON" -m pip install -q --no-cache-dir --user --upgrade "$PKG" > "$PIP_LOG" 2>&1; then
        INSTALLED=true
    fi
fi

# Strategy 3: --break-system-packages (Debian/Ubuntu externally-managed)
if [ "$INSTALLED" = false ]; then
    if "$PYTHON" -m pip install -q --no-cache-dir --break-system-packages --upgrade "$PKG" > "$PIP_LOG" 2>&1; then
        INSTALLED=true
    fi
fi

if [ "$INSTALLED" = false ]; then
    echo "ERROR: Could not install $PKG"
    echo "pip output:"
    cat "$PIP_LOG"
    echo ""
    echo "Run manually: $PYTHON -m pip install --no-cache-dir \"$PKG\""
    rm -f "$PIP_LOG"
    exit 1
fi

rm -f "$PIP_LOG"

# Save chain preference
mkdir -p "$HOME/.blockrun"
echo "$CHAIN" > "$HOME/.blockrun/.chain"

# ── Verify the package is importable ──────────────────────────────
if "$PYTHON" -c "import blockrun_llm; print(f'SDK v{blockrun_llm.__version__} installed')" 2>/dev/null; then
    # Run full verification
    "$PYTHON" - "$CHAIN" <<'PYEOF'
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
        print('Fix: pip install --no-cache-dir "blockrun-llm[solana]>=0.8.0"')
        sys.exit(1)
else:
    from blockrun_llm import setup_agent_wallet
    client = setup_agent_wallet(silent=True)
    addr = client.get_wallet_address()
    balance = client.get_balance()
    chain_label = "Base"
    fund_msg = "Fund wallet: Send USDC on Base to the address above"

print()
print(f'SocialClaw installed! (Chain: {chain_label})')
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
    # Package installed to a different python — tell user how to fix
    echo ""
    echo "SocialClaw skill cloned and chain preference saved."
    echo ""
    echo "NOTE: blockrun-llm was installed but $PYTHON can't find it."
    echo "This usually means you're using a virtual environment."
    echo "Run this in your active environment:"
    echo ""
    echo "  pip install --no-cache-dir \"$PKG\""
    echo ""
fi
