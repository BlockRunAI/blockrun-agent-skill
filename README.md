# SocialClaw

<div align="center">

<img src="assets/banner.png" alt="SocialClaw" width="600" />

<h3>Stop guessing what to post. Let your agent tell you.</h3>

<p>SocialClaw gives your AI agent real-time X/Twitter intelligence.<br>
One command → structured data → your agent acts on it. $0.08 per report.</p>

<br />

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-orange.svg)](https://github.com/anthropics/skills)
[![OpenAI Codex](https://img.shields.io/badge/OpenAI_Codex-Compatible-412991.svg)](https://openai.com/codex)
[![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-Compatible-4285F4.svg)](https://github.com/google-gemini/gemini-cli)
[![Cursor](https://img.shields.io/badge/Cursor-Compatible-000000.svg)](https://cursor.com)

[What Can I Do?](#what-can-i-do) · [Get Started](#get-started) · [Pricing](docs/pricing.md) · [API Reference](docs/api-reference.md)

</div>

---

## What Can I Do?

### Find out what to post right now

```bash
socialclaw radar "AI agents"
```

```
TRENDING NOW
  Anthropic          158 articles   115,983,616 views  <--
  Claude Code         29 articles    44,825,583 views
  Bitcoin             34 articles    27,136,645 views

LATEST TWEETS (42 found)
  @buildonsol     892 likes  "AI agents are about to change how we..."
    https://x.com/buildonsol/status/1234567890

SUGGESTED: Post your take on "Anthropic" — 115M views and climbing.
```

Your agent sees real view counts, finds the wave, and tells you exactly what to post about. No more scrolling Twitter for 45 minutes hoping for inspiration.

---

### Know who to engage with

```bash
socialclaw hitlist "Solana DeFi"
```

```
@solana_daily (45K followers) — 89 likes, climbing
  "Solana Projects to Watch this Week"
  https://x.com/solana_daily/status/123456789
  → Reply with specific data. Numbers get retweeted.

@DefiIgnas (240K followers) — 312 likes
  "Unpopular opinion: most AI agent tokens are..."
  https://x.com/DefiIgnas/status/987654321
  → Counter with your build story. Builders > speculators.
```

15 minutes replying to these 5 conversations > 1 hour writing a standalone tweet nobody sees. Your agent finds the high-leverage conversations for you.

---

### Understand any account in 10 seconds

```bash
socialclaw insight @jessepollak
```

```
PROFILE
  Followers:     347,004
  F/F Ratio:     72.3x (creator, not consumer)
  Verified:      Yes

TOP FOLLOWERS
  @coinbase           4,200,000 followers
  @brian_armstrong     1,800,000 followers

MENTION ENGAGEMENT
  Avg likes/mention:    23.4
  Total reach:          4,892
```

Before you DM someone, pitch them, or reply to their thread — know their actual influence, who follows them, and whether engaging with them is worth your time.

---

### Find the right people in any niche

```bash
socialclaw scout "x402 crypto"
```

```
TOP VOICES
  @jessepollak        347,004 followers — @base builder #001
  @BuildOnBase         89,200 followers — Official Base account
  @coinaborsh          45,190 followers — ecosystem builder
```

Building a product? Find the 10 people who actually matter in your space. Your agent identifies them by real engagement, not follower count.

---

### Compare yourself against competitors

```bash
socialclaw compare @you @competitor
```

```
METRIC               @you              @competitor
Followers             12,400              8,900
Mention likes          1,892              3,410
Avg likes/mention       12.3               28.4

QUICK TAKE: @competitor gets 2.3x more mention engagement despite fewer followers.
Their audience is more active. Study their reply strategy.
```

Stop wondering if you're winning. Know exactly where you stand and what to fix.

---

### Get your morning brief

```bash
socialclaw brief @yourhandle
```

```
3 new mentions overnight
  @HarryKamaAI (196K followers) mentioned you — reply within 30 minutes
  @defi_whale (45K) quote-tweeted your thread

TRENDING: "AI infrastructure" is spiking (28M views)

SUGGESTED ACTIONS:
  1. Reply to @HarryKamaAI (high-value mention, big audience)
  2. Post about AI infrastructure — ride the trend
  3. Thank @defi_whale for the QT — builds relationship
```

Wake up knowing exactly what happened and what to do first. Your agent monitors while you sleep.

---

### Look up any tweet or thread

```bash
socialclaw tweet https://x.com/elonmusk/status/1234567890
socialclaw thread https://x.com/VitalikButerin/status/9876543210
```

Get full tweet data, engagement metrics, replies, and complete threads — all structured, all actionable.

---

### Deep analytics on any creator

```bash
socialclaw analytics @VitalikButerin
```

Posting patterns, audience composition, engagement trajectory, content performance by topic. Everything you need to understand what makes an account grow.

---

## Get Started

**Claude Code** (one command):
```
try https://github.com/BlockRunAI/socialclaw
```

**Any agent / CLI**:
```bash
git clone https://github.com/BlockRunAI/socialclaw && cd socialclaw
bash install.sh                          # takeover mode, Base chain (default)
CHAIN=solana bash install.sh             # takeover mode, Solana chain
MODE=safe bash install.sh                # install only SocialClaw
MODE=force bash install.sh               # overwrite every sibling skill
bash install.sh --dry-run                # preview changes
bash install.sh --uninstall              # restore backups + remove launcher
```

This installs the skill, creates a `socialclaw` launcher in `~/.local/bin`, installs the SDK, and auto-detects your wallet.

Wallet auto-detected from `~/.*/*wallet*.json`. Fund with USDC. No API keys, no config, no signup.

---

## Why $0.08 beats $49/month

|  | Dashboard tools | SocialClaw |
|---|---|---|
| **You pay** | $49-99/month whether you use it or not | $0.08 per report, only when you need it |
| **You get** | Charts you read with your eyes | JSON your agent processes instantly |
| **You do** | Log in, click around, screenshot results | One function call, structured output |
| **Your agent can use it** | No (human-only UI) | Yes (that's the whole point) |
| **10 reports/day for a month** | $49/month | $24/month (and you keep the data) |
| **1 report this week** | Still $49/month | $0.08 total |

Every paid response is saved as JSON in `~/.blockrun/data/`. You paid for it — you keep it forever.

---

## Works With Every AI Agent

| Platform | How |
|----------|-----|
| **Claude Code** | Installs as a skill. Say "analyze @elonmusk on Twitter". |
| **OpenAI Codex** | Install `blockrun-llm>=0.8.0` for Base or `blockrun-llm[solana]>=0.8.0` for Solana. |
| **Gemini CLI** | Auto-installs to `~/.gemini/antigravity/skills/socialclaw`. |
| **Cursor / Windsurf** | Agent reads CLAUDE.md, calls SDK via terminal. |
| **Any terminal** | `socialclaw radar "topic"` |
| **Your own agent** | Use `LLMClient` on Base or `SolanaLLMClient` on Solana. |

---

## All Commands

| Command | What you get | Cost |
|---------|-------------|------|
| `insight @handle` | Full account analysis: profile, followers, mentions, tweets | ~$0.08 |
| `radar <topic>` | Trending topics + latest tweets + rising articles | ~$0.07 |
| `search <query>` | Search X with structured results + top tweets | ~$0.06 |
| `compare @a @b` | Side-by-side account comparison | ~$0.15 |
| `scout <topic>` | Find top voices in any niche | ~$0.07 |
| `hitlist <topic>` | High-engagement conversations to reply to | ~$0.03 |
| `audience @handle` | Follower segmentation by influence tier | ~$0.15 |
| `brief @handle` | Morning brief: mentions, trends, action items | ~$0.08 |
| `analytics @handle` | Deep author intelligence report | ~$0.02 |
| `tweet <id/url>` | Look up specific tweet + replies | ~$0.16 |
| `thread <id/url>` | Get full tweet thread | ~$0.03 |
| `engage @handle` | Find mentions + AI-generated reply drafts | ~$0.10 |
| `check @handle` | Verify posted tweets + engagement metrics | ~$0.05 |

---

## How It Works

- **No API keys.** Your USDC wallet IS your authentication (x402 protocol).
- **No subscriptions.** Pay per call. $1 = ~12 full reports.
- **Private key stays local.** Only signatures are sent over the wire.
- **Base or Solana.** Your choice. Same SDK, same endpoints.
- **Data is yours.** Every response saved to `~/.blockrun/data/`.

[Full API Reference](docs/api-reference.md) · [Pricing details](docs/pricing.md)

---

## From the BlockRun Ecosystem

<table>
<tr>
<td width="50%">

### SocialClaw
**X/Twitter intelligence for your agent**

You're here. One function call = one intelligence report. $0.08, not $49/month.

`bash install.sh` or `CHAIN=solana bash install.sh`

</td>
<td width="50%">

### [ClawRouter](https://github.com/BlockRunAI/ClawRouter)
**LLM router for autonomous agents**

41+ models, smart routing, x402 USDC payments. Your agent picks the best model at the best price automatically.

`curl -fsSL https://blockrun.ai/ClawRouter-update | bash`

[![GitHub stars](https://img.shields.io/github/stars/BlockRunAI/ClawRouter?style=flat-square)](https://github.com/BlockRunAI/ClawRouter)

</td>
</tr>
</table>

> **Together:** SocialClaw pulls the intelligence. ClawRouter routes your LLM calls. Same wallet, same payment layer. Your agent's full stack.

---

<div align="center">

**[blockrun.ai](https://blockrun.ai)** · **[AttentionVC](https://attentionvc.com)** · **[x402 Protocol](https://x402.org)** · **[hello@blockrun.ai](mailto:hello@blockrun.ai)**

Powered by [BlockRun](https://blockrun.ai) × [AttentionVC](https://attentionvc.com) · MIT

</div>
