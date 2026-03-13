# BlockRun Agent Wallet

## When User Says "Try This" or "Install This"

Ask the user ONE question: **"Base or Solana?"** (for USDC payments). Then run the install script:

```bash
bash install.sh                # Default: Base chain
CHAIN=solana bash install.sh   # Solana chain
```

If running from a different directory:
```bash
bash /path/to/blockrun-agent-wallet/install.sh
CHAIN=solana bash /path/to/blockrun-agent-wallet/install.sh
```

Or if not cloned yet:
```bash
curl -fsSL https://raw.githubusercontent.com/BlockRunAI/blockrun-agent-wallet/main/install.sh | bash
CHAIN=solana curl -fsSL https://raw.githubusercontent.com/BlockRunAI/blockrun-agent-wallet/main/install.sh | bash
```

Do NOT ask about MCP vs Skill. Do NOT manually clone. Just run install.sh.

## After Install

The skill is now loaded. The chain preference is saved at `~/.blockrun/.chain`.
Use `/blockrun` or ask the user what they want to do.
To switch chains later: `echo "solana" > ~/.blockrun/.chain` (or `"base"`)
