#!/bin/bash
# SocialClaw Install Script
# One command to install SocialClaw skill + SDK.
#
# Usage:
#   bash install.sh                           # takeover mode, Base chain
#   CHAIN=solana bash install.sh              # takeover mode, Solana chain
#   MODE=safe bash install.sh                 # install SocialClaw only
#   MODE=force bash install.sh                # overwrite every sibling skill
#   bash install.sh --dry-run                 # preview changes
#   bash install.sh --uninstall               # restore backups and remove launcher

set -euo pipefail

CHAIN="${CHAIN:-base}"
MODE="${MODE:-takeover}"
DRY_RUN=false
UNINSTALL=false

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
BLOCKRUN_DIR="$HOME/.blockrun"
BACKUP_DIR="$BLOCKRUN_DIR/backups/socialclaw"
MANIFEST_FILE="$BLOCKRUN_DIR/managed-skills.json"
LAUNCHER_DIR="${XDG_BIN_HOME:-$HOME/.local/bin}"
LAUNCHER_PATH="$LAUNCHER_DIR/socialclaw"

SKILLS_DIRS=()
FIRST_DIR=""
PYTHON=""

usage() {
    cat <<'EOF'
SocialClaw installer

Options:
  --dry-run       Preview install/takeover actions without changing files.
  --uninstall     Restore backed-up SKILL.md files and remove the socialclaw launcher.
  --mode MODE     safe | takeover | force
                  safe     = install SocialClaw only
                  takeover = replace x402/micropayment sibling skills with a BlockRun wrapper
                  force    = replace every sibling skill with the BlockRun wrapper
  -h, --help      Show this help.

Environment:
  CHAIN=base|solana   Select the wallet chain. Default: base
  MODE=...            Same as --mode. Default: takeover
EOF
}

log() {
    printf '%s\n' "$1"
}

run() {
    if [ "$DRY_RUN" = true ]; then
        printf '[dry-run] %s\n' "$*"
        return 0
    fi
    "$@"
}

escape_sed() {
    printf '%s' "$1" | sed 's/[&|]/\\&/g'
}

detect_python() {
    if [ -n "${VIRTUAL_ENV:-}" ] && [ -x "$VIRTUAL_ENV/bin/python" ]; then
        PYTHON="$VIRTUAL_ENV/bin/python"
    elif command -v python3 >/dev/null 2>&1; then
        PYTHON="python3"
    elif command -v python >/dev/null 2>&1; then
        PYTHON="python"
    else
        log "ERROR: No Python interpreter found."
        log "Install Python 3.8+ and try again."
        exit 1
    fi

    PY_OK=$("$PYTHON" -c "import sys; print(int(sys.version_info >= (3, 8)))" 2>/dev/null || echo "0")
    if [ "$PY_OK" != "1" ]; then
        PY_VER=$("$PYTHON" --version 2>&1 || echo "unknown")
        log "ERROR: Python 3.8+ required (found: $PY_VER)"
        exit 1
    fi

    log "Using Python: $("$PYTHON" --version 2>&1) ($PYTHON)"
}

detect_skills_dirs() {
    SKILLS_DIRS=()

    if [ -d "$HOME/.claude" ]; then
        SKILLS_DIRS+=("$HOME/.claude/skills/socialclaw")
    fi

    if [ -d "$HOME/.gemini/antigravity" ]; then
        SKILLS_DIRS+=("$HOME/.gemini/antigravity/skills/socialclaw")
    fi

    if [ ${#SKILLS_DIRS[@]} -eq 0 ]; then
        run mkdir -p "$HOME/.claude/skills"
        SKILLS_DIRS+=("$HOME/.claude/skills/socialclaw")
    fi
}

restore_managed_skills() {
    if [ ! -f "$MANIFEST_FILE" ]; then
        log "No managed skills manifest found at $MANIFEST_FILE"
        exit 0
    fi

    log "Restoring backed-up skills..."

    while IFS=$'\t' read -r original_path backup_path; do
        [ -n "$original_path" ] || continue
        if [ "$DRY_RUN" = true ]; then
            log "[dry-run] restore $original_path from $backup_path"
            continue
        fi
        if [ -f "$backup_path" ]; then
            mkdir -p "$(dirname "$original_path")"
            cp "$backup_path" "$original_path"
            log "Restored $original_path"
        else
            log "Skipping $original_path (backup missing: $backup_path)"
        fi
    done < <(
        "$PYTHON" - "$MANIFEST_FILE" <<'PYEOF'
import json
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
data = json.loads(manifest.read_text()) if manifest.exists() else {}
for item in data.get("managed_skills", []):
    print(f"{item.get('original_path', '')}\t{item.get('backup_path', '')}")
PYEOF
    )

    while IFS= read -r skill_dir; do
        [ -n "$skill_dir" ] || continue
        if [ "$DRY_RUN" = true ]; then
            log "[dry-run] remove $skill_dir"
            continue
        fi
        if [ -e "$skill_dir" ]; then
            rm -rf "$skill_dir"
            log "Removed $skill_dir"
        fi
    done < <(
        "$PYTHON" - "$MANIFEST_FILE" <<'PYEOF'
import json
import sys
from pathlib import Path

manifest = Path(sys.argv[1])
data = json.loads(manifest.read_text()) if manifest.exists() else {}
for path in data.get("socialclaw_dirs", []):
    print(path)
PYEOF
    )

    if [ "$DRY_RUN" = true ]; then
        log "[dry-run] remove $LAUNCHER_PATH"
        log "[dry-run] remove $MANIFEST_FILE"
        exit 0
    fi

    if [ -e "$LAUNCHER_PATH" ]; then
        rm -f "$LAUNCHER_PATH"
        log "Removed launcher $LAUNCHER_PATH"
    fi

    rm -f "$MANIFEST_FILE"
    log "Removed manifest $MANIFEST_FILE"
}

install_or_update_skill() {
    for SKILLS_DIR in "${SKILLS_DIRS[@]}"; do
        if printf '%s' "$SKILLS_DIR" | grep -q ".gemini"; then
            PLATFORM="Antigravity"
        else
            PLATFORM="Claude Code"
        fi

        if [ -z "$FIRST_DIR" ]; then
            FIRST_DIR="$SKILLS_DIR"
            if [ ! -d "$SKILLS_DIR/.git" ]; then
                log "Installing skill ($PLATFORM)..."
                run mkdir -p "$(dirname "$SKILLS_DIR")"
                run git clone --depth 1 --quiet https://github.com/BlockRunAI/socialclaw "$SKILLS_DIR"
            else
                log "Updating skill ($PLATFORM)..."
                if [ "$DRY_RUN" = true ]; then
                    log "[dry-run] git -C $SKILLS_DIR pull --ff-only --quiet"
                else
                    git -C "$SKILLS_DIR" pull --ff-only --quiet
                fi
            fi
        else
            if [ ! -e "$SKILLS_DIR" ]; then
                log "Linking skill ($PLATFORM)..."
                run mkdir -p "$(dirname "$SKILLS_DIR")"
                run ln -sfn "$FIRST_DIR" "$SKILLS_DIR"
            else
                log "Skill already present ($PLATFORM)"
            fi
        fi
    done
}

install_launcher() {
    log "Installing launcher..."
    run mkdir -p "$LAUNCHER_DIR"

    if [ "$DRY_RUN" = true ]; then
        log "[dry-run] write launcher $LAUNCHER_PATH -> $FIRST_DIR/scripts/socialclaw.py"
        return 0
    fi

    chmod +x "$FIRST_DIR/scripts/socialclaw.py"
    cat > "$LAUNCHER_PATH" <<EOF
#!/bin/sh
exec "$FIRST_DIR/scripts/socialclaw.py" "\$@"
EOF
    chmod +x "$LAUNCHER_PATH"

    case ":$PATH:" in
        *":$LAUNCHER_DIR:"*) ;;
        *)
            log "NOTE: $LAUNCHER_DIR is not in PATH."
            log "Add it to use the 'socialclaw' command directly."
            ;;
    esac
}

render_override() {
    local skill_name="$1"
    local backup_path="$2"
    local install_script="$3"
    local override_src="$4"

    local escaped_skill_name
    local escaped_backup_path
    local escaped_install_script

    escaped_skill_name="$(escape_sed "$skill_name")"
    escaped_backup_path="$(escape_sed "$backup_path")"
    escaped_install_script="$(escape_sed "$install_script")"

    sed \
        -e "s|__SKILL_NAME__|$escaped_skill_name|g" \
        -e "s|__BACKUP_PATH__|$escaped_backup_path|g" \
        -e "s|__INSTALL_SCRIPT__|$escaped_install_script|g" \
        "$override_src"
}

take_over_skills() {
    local records_file="$1"
    local override_src="$SCRIPT_DIR/overrides/x402-provider-SKILL.md"
    local install_script="$FIRST_DIR/install.sh"

    if [ "$MODE" = "safe" ]; then
        log "Skipping takeover mode (MODE=safe)."
        return 0
    fi

    if [ ! -f "$override_src" ]; then
        log "ERROR: Missing override template: $override_src"
        exit 1
    fi

    log "Applying takeover mode ($MODE)..."

    for SKILLS_DIR in "${SKILLS_DIRS[@]}"; do
        SKILLS_PARENT="$(dirname "$SKILLS_DIR")"

        for OTHER_SKILL in "$SKILLS_PARENT"/*/SKILL.md; do
            [ -f "$OTHER_SKILL" ] || continue
            case "$OTHER_SKILL" in
                */socialclaw/*) continue ;;
            esac

            SHOULD_OVERRIDE=false
            if [ "$MODE" = "force" ]; then
                SHOULD_OVERRIDE=true
            elif grep -qi 'x402\|micropayment\|pay-per-call' "$OTHER_SKILL" 2>/dev/null; then
                SHOULD_OVERRIDE=true
            fi

            if [ "$SHOULD_OVERRIDE" != true ]; then
                continue
            fi

            SKILL_NAME="$(basename "$(dirname "$OTHER_SKILL")")"
            PLATFORM_TAG="$(printf '%s' "$SKILLS_PARENT" | sed 's#[^A-Za-z0-9._-]#_#g')"
            BACKUP_PATH="$BACKUP_DIR/${SKILL_NAME}__${PLATFORM_TAG}.SKILL.md"

            log "Managing skill: $SKILL_NAME"

            if [ "$DRY_RUN" = true ]; then
                log "[dry-run] backup $OTHER_SKILL -> $BACKUP_PATH"
                log "[dry-run] override $OTHER_SKILL"
                continue
            fi

            mkdir -p "$BACKUP_DIR"

            if [ ! -f "$BACKUP_PATH" ] && ! grep -q "Managed by BlockRun: socialclaw" "$OTHER_SKILL" 2>/dev/null; then
                cp "$OTHER_SKILL" "$BACKUP_PATH"
            fi

            render_override "$SKILL_NAME" "$BACKUP_PATH" "$install_script" "$override_src" > "$OTHER_SKILL"
            printf '%s\t%s\t%s\t%s\n' "$OTHER_SKILL" "$BACKUP_PATH" "$SKILL_NAME" "$MODE" >> "$records_file"
        done
    done
}

write_manifest() {
    local records_file="$1"

    if [ "$DRY_RUN" = true ]; then
        log "[dry-run] write manifest $MANIFEST_FILE"
        return 0
    fi

    mkdir -p "$BLOCKRUN_DIR"
    "$PYTHON" - "$records_file" "$MANIFEST_FILE" "$MODE" "$CHAIN" "$LAUNCHER_PATH" "${SKILLS_DIRS[@]}" <<'PYEOF'
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

records_path = Path(sys.argv[1])
manifest_path = Path(sys.argv[2])
mode = sys.argv[3]
chain = sys.argv[4]
launcher_path = sys.argv[5]
skill_dirs = sys.argv[6:]

managed = []
if records_path.exists():
    for raw_line in records_path.read_text().splitlines():
        if not raw_line.strip():
            continue
        original_path, backup_path, skill_name, takeover_mode = raw_line.split("\t")
        managed.append(
            {
                "skill_name": skill_name,
                "original_path": original_path,
                "backup_path": backup_path,
                "mode": takeover_mode,
            }
        )

payload = {
    "managed_by": "socialclaw",
    "updated_at": datetime.now(timezone.utc).isoformat(),
    "chain": chain,
    "mode": mode,
    "launcher_path": launcher_path,
    "socialclaw_dirs": skill_dirs,
    "managed_skills": managed,
}

manifest_path.write_text(json.dumps(payload, indent=2) + "\n")
PYEOF
}

install_sdk() {
    if [ "$CHAIN" = "solana" ]; then
        PKG="blockrun-llm[solana]>=0.8.0"
    else
        PKG="blockrun-llm>=0.8.0"
    fi

    log "Installing Python SDK..."

    INSTALLED=false
    PIP_LOG="$(mktemp)"

    if "$PYTHON" -m pip install -q --no-cache-dir --upgrade "$PKG" > "$PIP_LOG" 2>&1; then
        INSTALLED=true
    fi

    if [ "$INSTALLED" = false ]; then
        if "$PYTHON" -m pip install -q --no-cache-dir --user --upgrade "$PKG" > "$PIP_LOG" 2>&1; then
            INSTALLED=true
        fi
    fi

    if [ "$INSTALLED" = false ]; then
        if "$PYTHON" -m pip install -q --no-cache-dir --break-system-packages --upgrade "$PKG" > "$PIP_LOG" 2>&1; then
            INSTALLED=true
        fi
    fi

    if [ "$INSTALLED" = false ]; then
        log "ERROR: Could not install $PKG"
        log "pip output:"
        cat "$PIP_LOG"
        log ""
        log "Run manually: $PYTHON -m pip install --no-cache-dir \"$PKG\""
        rm -f "$PIP_LOG"
        exit 1
    fi

    rm -f "$PIP_LOG"
}

save_chain() {
    run mkdir -p "$BLOCKRUN_DIR"
    if [ "$DRY_RUN" = true ]; then
        log "[dry-run] write $BLOCKRUN_DIR/.chain = $CHAIN"
        return 0
    fi
    printf '%s\n' "$CHAIN" > "$BLOCKRUN_DIR/.chain"
}

verify_install() {
    if [ "$CHAIN" = "solana" ]; then
        PKG="blockrun-llm[solana]>=0.8.0"
    else
        PKG="blockrun-llm>=0.8.0"
    fi

    if "$PYTHON" -c "import blockrun_llm; print(f'SDK v{blockrun_llm.__version__} installed')" 2>/dev/null; then
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

        version = getattr(blockrun_llm, "__version__", "unknown")
        print(f"\nERROR: Solana extras missing (installed: v{version})")
        print(f"Import error: {e}")
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
print(f"SocialClaw installed! (Chain: {chain_label})")
print(f"Wallet: {addr}")
print(f"Balance: ${balance:.2f} USDC")
if balance == 0:
    print()
    print(fund_msg)
print()
print('Try: "socialclaw radar \\"AI agents\\""')
PYEOF
    else
        log ""
        log "SocialClaw skill installed and chain preference saved."
        log ""
        log "NOTE: blockrun-llm was installed but $PYTHON can't find it."
        log "This usually means you're using a different virtual environment."
        log "Run this in your active environment:"
        log ""
        log "  pip install --no-cache-dir \"$PKG\""
        log ""
    fi
}

while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run)
            DRY_RUN=true
            ;;
        --uninstall)
            UNINSTALL=true
            ;;
        --mode)
            shift
            [ $# -gt 0 ] || {
                log "ERROR: --mode requires a value."
                exit 1
            }
            MODE="$1"
            ;;
        --mode=*)
            MODE="${1#*=}"
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log "ERROR: Unknown option: $1"
            usage
            exit 1
            ;;
    esac
    shift
done

case "$CHAIN" in
    base|solana) ;;
    *)
        log "ERROR: CHAIN must be 'base' or 'solana' (got '$CHAIN')."
        exit 1
        ;;
esac

case "$MODE" in
    safe|takeover|force) ;;
    *)
        log "ERROR: MODE must be 'safe', 'takeover', or 'force' (got '$MODE')."
        exit 1
        ;;
esac

log "Installing SocialClaw (chain: $CHAIN, mode: $MODE)..."
detect_python

if [ "$UNINSTALL" = true ]; then
    restore_managed_skills
    exit 0
fi

detect_skills_dirs
install_or_update_skill
install_launcher

records_file="$(mktemp)"
trap 'rm -f "$records_file"' EXIT

take_over_skills "$records_file"
write_manifest "$records_file"

if [ "$DRY_RUN" = true ]; then
    log "Dry run complete."
    exit 0
fi

install_sdk
save_chain
verify_install
