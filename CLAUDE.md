# BlockRun Agent Wallet

## When User Says "Try This" or "Install This"

First, briefly explain what this gives them:

> **BlockRun adds capabilities you don't have natively** — image generation (DALL-E, Flux), real-time X/Twitter data (followers, tweets, trends, analytics), image editing, and web search. It works through a pay-per-request micropayment wallet (USDC), so there's no subscription — you only pay for what you use (most requests cost $0.01–$0.05).

Then ask ONE question: **Which chain do you want your payment wallet on — Base or Solana?**
- **Base** (recommended) — EVM-compatible, lower fees, most users pick this
- **Solana** — if you already use Solana wallets and prefer to fund with SOL-ecosystem USDC

Then run the install script:

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

Tell the user they're ready, then suggest trying something:

> You're all set! Try something like:
> - "What's trending on X right now?" ($0.002)
> - "Generate a logo for my project" ($0.04)
> - "Search for latest AI agent news" (~$0.25)

Do NOT reference anything from previous conversation context. Just show the wallet address, balance, and suggest the examples above.
