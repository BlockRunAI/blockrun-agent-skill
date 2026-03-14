# SocialClaw

<div align="center">

<img src="assets/banner.png" alt="SocialClaw" width="600" />

<h3>X/Twitter Marketing Intelligence for AI Agents</h3>

<p>Turn real-time X/Twitter data into growth strategy — account insights, competitor analysis, audience mapping, KOL discovery, and daily briefs. Works with any AI coding agent.</p>

<br />

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-orange.svg)](https://github.com/anthropics/skills)
[![OpenAI Codex](https://img.shields.io/badge/OpenAI_Codex-Compatible-412991.svg)](https://openai.com/codex)
[![Gemini CLI](https://img.shields.io/badge/Gemini_CLI-Compatible-4285F4.svg)](https://github.com/google-gemini/gemini-cli)
[![Cursor](https://img.shields.io/badge/Cursor-Compatible-000000.svg)](https://cursor.com)
[![No API Keys](https://img.shields.io/badge/API_Keys-None_Required-brightgreen.svg)](https://blockrun.ai)
[![USDC](https://img.shields.io/badge/Pay_with-USDC-2775CA.svg)](https://blockrun.ai)
[![Base](https://img.shields.io/badge/Base-Chain-0052FF.svg)](https://base.org)
[![Solana](https://img.shields.io/badge/Solana-Chain-9945FF.svg)](https://solana.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Get Started](#get-started) · [Workflows](#workflows) · [API Reference](#api-reference) · [Pricing](#pricing)

</div>

---

## Why SocialClaw?

|  | X API (Official) | Third-party tools | **SocialClaw** |
|--|-----------------|-------------------|----------------|
| Cost | $100+/month | $50-200/month | **$0.03-0.15 per report** |
| API keys | Required | Required | **None** |
| Setup time | Hours | Minutes | **Seconds** |
| Works in terminal | No | No | **Yes** |
| AI agent native | No | No | **Yes** |
| Pay-as-you-go | No | No | **Yes** |
| Data saved locally | No | No | **Yes** |

**$1 USDC = ~12 full marketing reports.** No subscriptions. No API keys. Just results.

---

## Get Started

**Claude Code:**
```
try https://github.com/BlockRunAI/socialclaw
```

**Codex / Cursor / any agent:**
```bash
pip install blockrun-llm[solana]
```

**CLI:**
```bash
git clone https://github.com/BlockRunAI/socialclaw && cd socialclaw
pip install blockrun-llm[solana]
python scripts/socialclaw.py insight @anyuser
```

SocialClaw auto-detects any USDC wallet in your `~/` directory — Base or Solana. No config needed.

---

## Workflows

Seven marketing workflows that chain multiple API calls into actionable intelligence.

| # | Workflow | What it does | Cost |
|---|---------|-------------|------|
| 1 | [**Insight**](#1-insight--account-deep-dive) | Full account analysis — profile, mentions, top followers | ~$0.08 |
| 2 | [**Radar**](#2-radar--topic-intelligence) | What's trending, what's working, where to post | ~$0.07 |
| 3 | [**Compare**](#3-compare--competitor-analysis) | Side-by-side competitor breakdown | ~$0.15 |
| 4 | [**Audience**](#4-audience--follower-segmentation) | Who follows them? Segment by influence tier | ~$0.15 |
| 5 | [**Scout**](#5-scout--kol-discovery) | Find top voices in any topic | ~$0.07 |
| 6 | [**Hitlist**](#6-hitlist--engagement-targets) | High-value conversations to join right now | ~$0.03 |
| 7 | [**Brief**](#7-brief--daily-marketing-report) | Morning report: mentions + trends + actions | ~$0.08 |

---

### 1. Insight — Account Deep-Dive

> _Who is this account? What's their influence? Who's talking about them?_

```
socialclaw insight @jessepollak
```

<details>
<summary>Example output</summary>

```
  PROFILE
  Name:          jesse.base.eth
  Followers:     347,004
  Verified:      Yes
  F/F Ratio:     78.7x

  MENTIONS (20 recent)
    @aiven_io         41 likes  3 RTs  Fully managed Kafka environment...
    @marcopolo2027     0 likes  0 RTs  this is the future for @base app

  TOP FOLLOWERS (by influence)
    @alloxdotai              131,567 followers
    @AprilCumberland          60,265 followers
    @ellazhang516             38,968 followers

  MENTION ENGAGEMENT
    Avg likes per mention:    2.8
    Total reach:              59

  Cost: $0.08 (3 calls)
```

</details>

**Chains:** `users/info` → `users/mentions` → `users/followers`
**Output:** Profile stats, F/F ratio, mention sentiment, top followers ranked by influence.

---

### 2. Radar — Topic Intelligence

> _What's hot? What content format is working? Where should I jump in?_

```
socialclaw radar "AI agents"
```

<details>
<summary>Example output</summary>

```
  TRENDING NOW
    Anthropic          158 articles   115,983,616 views
    OpenAI              48 articles    51,378,182 views
    Claude Code         29 articles    44,825,583 views
    Bitcoin              34 articles    27,136,645 views

  LATEST TWEETS (20 found)
    @Computerworld  [0 likes] Microsoft shuffles leadership as Copilot and AI agents...
    @badlogicgames  [5 likes] pi now has feature parity with other agents from July 2025...
    @_agslabs       [1 likes] Indian builders — hackathon wave is LIVE!

  RISING ARTICLES
    [viral] "One day" — https://x.com/Tad_2/status/...

  TOPIC PULSE
    Total engagement (latest 20 tweets): 9
    Avg likes per tweet: 0.5

  Cost: $0.07 (4 calls)
```

</details>

**Chains:** `trending` → `search (Latest)` → `search (Top)` → `articles/rising`
**Output:** Trending topics with views, latest conversation, top tweets, viral content, content opportunity signals.

---

### 3. Compare — Competitor Analysis

> _Side-by-side: who's winning and why?_

```
socialclaw compare @jessepollak @VitalikButerin
```

<details>
<summary>Example output</summary>

```
  METRIC              @jessepollak    @VitalikButerin
  ─────────────────────────────────────────────────────
  Followers              347,004         5,800,000
  Following                4,406            ~3,000
  Tweets                  57,569           ~15,000
  Verified                   Yes               Yes
  F/F Ratio               78.7x            ~1900x

  MENTIONS              @jessepollak    @VitalikButerin
  ─────────────────────────────────────────────────────
  Recent mentions              20                20
  Total likes                  56                 7
  Avg likes/mention           2.8               0.3

  TOP FOLLOWERS
  @jessepollak:
    @alloxdotai              131,567
    @AprilCumberland          60,265
  @VitalikButerin:
    @HerawanBoma                 525
    @GoXrp                       339

  QUICK TAKE
    @VitalikButerin has 16.7x more followers
    @jessepollak gets more mention engagement (59 vs 7)

  Cost: $0.15 (6 calls)
```

</details>

**Chains:** `users/info` ×2 → `users/mentions` ×2 → `users/followers` ×2
**Output:** Followers, posting frequency, engagement, audience quality, who has momentum.

---

### 4. Audience — Follower Segmentation

> _Who follows them? Cluster by influence tier and interests._

```
socialclaw audience @jessepollak
```

<details>
<summary>Example output</summary>

```
  MEGA INFLUENCERS (100K+ followers): 2
    @alloxdotai: 131,567 — AI & DeFi infrastructure
    @AprilCumberland: 60,265 — Crypto venture partner

  MACRO (10K-100K): 8
    @ellazhang516, @zbktnumberone, @EtherBubu...

  MICRO (1K-10K): 15

  COMMON THEMES IN BIOS
    "crypto", "web3", "builder", "defi", "base"

  Cost: $0.15 (3 calls)
```

</details>

**Chains:** `users/followers` → `users/lookup` (batch top 50) → segment + analyze bios
**Output:** Audience tiers (mega/macro/micro), common interests, potential partners.

---

### 5. Scout — KOL Discovery

> _Find the key voices in any topic — ranked by influence, ready for outreach._

```
socialclaw scout "base blockchain"
```

<details>
<summary>Example output</summary>

```
  TOP VOICES ON "base blockchain"
    @jessepollak            347,004 followers — @base builder #001
    @BuildOnBase             89,200 followers — Official Base account
    @coinaborsh              45,000 followers — Base ecosystem analyst
    @web3marketer            23,400 followers — Growth at Base projects
    @basedbuilder            12,100 followers — Shipping on Base daily

  Cost: $0.07 (2 calls)
```

</details>

**Chains:** `search` → extract unique authors → `users/lookup` (batch) → rank by followers
**Output:** Ranked influencer list with follower counts and bios.

---

### 6. Hitlist — Engagement Targets

> _High-value conversations happening RIGHT NOW. Jump in._

```
socialclaw hitlist "AI agents crypto"
```

<details>
<summary>Example output</summary>

```
  ENGAGEMENT TARGETS
    @solana_daily (45K followers) — 14 likes
      "Solana Projects to Watch this Week: @anagramxyz @BlockRunAI..."
      → Reply angle: share your project's latest update

    @A47X124 (12K followers) — 8 likes
      "The ones not on these lists are usually the ones that surprise..."
      → Reply angle: agree + highlight an unlisted project

    @taowang1 (8K followers) — 4 likes
      "@CoinbaseDev @BlockRunAI Please include $fxUSD"
      → Reply angle: join the ecosystem conversation

  Cost: $0.03 (1 call)
```

</details>

**Chains:** `search` → sort by (engagement × author influence)
**Output:** Ranked conversations to join, with suggested reply angles. Cheapest workflow.

---

### 7. Brief — Daily Marketing Report

> _What happened overnight? What should I post today?_

```
socialclaw brief @blockrunai
```

<details>
<summary>Example output</summary>

```
  YOUR MENTIONS (5 new)
    @KashKysh: Let's watch closely folks
    @Rich_lifee_: They are the ones that end up with the biggest...

  TRENDING NOW
    Anthropic          158 articles   115M views
    OpenAI              48 articles    51M views
    Claude Code         29 articles    44M views

  RISING CONTENT
    "AI agents reshape products" — going viral on X

  SUGGESTED ACTIONS
    1. Reply to @Rich_lifee_ — talking about you to 5K followers
    2. Create content around "Anthropic" trend (115M views today)
    3. Share perspective on rising "AI agents" article

  Cost: $0.08 (3 calls)
```

</details>

**Chains:** `users/mentions` → `trending` → `articles/rising`
**Output:** Morning brief with mentions, trends, and 3 concrete actions.

---

## API Reference

All data through [BlockRun](https://blockrun.ai)'s unified gateway, powered by [AttentionVC](https://attentionvc.com).

### X/Twitter Data (16 endpoints)

| Method | What | Cost |
|--------|------|------|
| `x_user_info(username)` | Profile, bio, stats, verification | $0.002 |
| `x_user_lookup([users])` | Batch profiles, up to 100 | $0.002/user |
| `x_followers(username)` | Follower list ~200/page | $0.05/page |
| `x_followings(username)` | Following list ~200/page | $0.05/page |
| `x_verified_followers(user_id)` | Blue-check followers only | $0.048/page |
| `x_user_tweets(username)` | User's tweets + engagement | $0.032/page |
| `x_user_mentions(username)` | Tweets mentioning user | $0.032/page |
| `x_search(query)` | Search tweets, Latest or Top | $0.032/page |
| `x_trending()` | Trending topics + view counts | $0.002 |
| `x_articles_rising()` | Viral content detection | $0.05 |
| `x_tweet_lookup([ids])` | Batch tweet data, up to 200 | $0.16/batch |
| `x_tweet_replies(tweet_id)` | Replies to a tweet | $0.032/page |
| `x_tweet_thread(tweet_id)` | Full conversation thread | $0.032/page |
| `x_author_analytics(handle)` | Author intelligence score | $0.02 |
| `x_compare_authors(h1, h2)` | Compare two accounts | $0.05 |

### AI Models

| Method | What | Cost |
|--------|------|------|
| `chat(model, prompt)` | GPT-5.2, Grok, DeepSeek, Claude, Gemini | varies |
| `chat(model, prompt, search=True)` | Grok with live X/Twitter search | ~$0.25 |
| `search(query)` | Web + X + news search | ~$0.25 |
| `generate(prompt)` | Image generation (DALL-E, Nano Banana) | $0.01-0.04 |
| `image_edit(prompt, image)` | Image editing | $0.02-0.04 |

### 30+ LLM Models Available

| Model | Best for | Input | Output |
|-------|----------|-------|--------|
| `openai/gpt-5.2` | General, code review | $1.75/M | $14.00/M |
| `openai/gpt-5-mini` | Fast + cheap | $0.30/M | $1.20/M |
| `xai/grok-3` | Real-time X data | $3.00/M | $15.00/M |
| `deepseek/deepseek-chat` | Bulk processing | $0.28/M | $0.42/M |
| `anthropic/claude-sonnet-4` | Coding | $3.00/M | $15.00/M |
| `google/gemini-2.5-flash` | Long documents | $0.15/M | $0.60/M |

---

## Pricing

### Workflow Costs

| Workflow | API Calls | Cost | What $1 gets you |
|----------|-----------|------|-----------------|
| Insight | 3 calls | ~$0.08 | 12 reports |
| Radar | 4 calls | ~$0.07 | 14 reports |
| Compare | 6 calls | ~$0.15 | 6 reports |
| Audience | 3 calls | ~$0.15 | 6 reports |
| Scout | 2 calls | ~$0.07 | 14 reports |
| Hitlist | 1 call | ~$0.03 | 33 reports |
| Brief | 3 calls | ~$0.08 | 12 reports |

### vs. Alternatives

| What you need | X API Official | SocialClaw |
|--------------|---------------|------------|
| 1 profile lookup | $100/month subscription | **$0.002** |
| 1,000 follower profiles | $100/month subscription | **$0.25** |
| Trending topics | $100/month subscription | **$0.002** |
| Full competitor report | $100/month + build it yourself | **$0.15** |

---

## How It Works

```
        ┌─────────────────────────────────────┐
        │  "analyze @competitor's X presence"  │
        └──────────────────┬──────────────────┘
                           │
            ┌──────────────▼──────────────┐
            │   SocialClaw finds wallet   │
            │  ~/.<any>/solana-wallet.json │
            │  ~/.<any>/wallet.json        │
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │  Calls BlockRun API gateway  │
            │  x402 USDC micropayment     │
            │  Private key stays local    │
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │  Data saved to              │
            │  ~/.blockrun/data/          │
            │  (you paid for it, keep it) │
            └──────────────┬──────────────┘
                           │
            ┌──────────────▼──────────────┐
            │  Actionable marketing       │
            │  intelligence report        │
            └─────────────────────────────┘
```

### Payment

- **Protocol:** [x402](https://x402.org) — HTTP 402 micropayments
- **Currency:** USDC on [Base](https://base.org) or [Solana](https://solana.com)
- **Security:** Private key never leaves your machine. Only cryptographic signatures are transmitted — same as signing a MetaMask transaction.

### Wallet Auto-Detection

SocialClaw scans `~/.<any-folder>/` for `wallet.json` or `solana-wallet.json`. Compatible with:

- [AgentCash](https://agentcash.dev) wallets
- x402 wallets
- Any wallet using the standard `{"privateKey": "...", "address": "..."}` format

### Data Persistence

Every API response saved as timestamped JSON:

```
~/.blockrun/data/
├── 20260314_030816_trending.json
├── 20260314_030820_search_blockrunai.json
├── 20260314_025259_mentions_jessepollak.json
└── 20260314_030502_followers_VitalikButerin.json
```

---

## Works With Every AI Coding Agent

SocialClaw is a Python SDK + skill definition. It works anywhere Python runs — which means every major AI agent platform.

| Platform | Install | How it works |
|----------|---------|-------------|
| **Claude Code** | `try https://github.com/BlockRunAI/socialclaw` | Loads as a Claude Code skill. Agent reads SKILL.md, calls SDK automatically. |
| **OpenAI Codex** | `pip install blockrun-llm[solana]` | Codex executes Python in sandbox. Import SDK, run workflows. |
| **Gemini CLI / Antigravity** | `git clone ... ~/.gemini/antigravity/skills/socialclaw` | Loads as Antigravity skill. Same SDK, same workflows. |
| **Cursor / Windsurf** | `pip install blockrun-llm[solana]` | Agent reads CLAUDE.md for context, calls SDK via terminal. |
| **Any terminal** | `python scripts/socialclaw.py insight @user` | Direct CLI. No agent needed. |
| **Your own agent** | `from blockrun_llm import SolanaLLMClient` | Import as a library. Build custom workflows. |

**Why it works everywhere:** SocialClaw is just Python + a wallet. No platform-specific APIs, no cloud dependencies, no auth servers. The SDK handles x402 payment signing locally and talks directly to BlockRun's gateway. Any agent that can run `pip install` and execute Python can use it.

---

## Contributing

SocialClaw is open source. PRs welcome.

```bash
git clone https://github.com/BlockRunAI/socialclaw
cd socialclaw
pip install blockrun-llm[solana]
python scripts/socialclaw.py radar "your topic"
```

---

<div align="center">

**[blockrun.ai](https://blockrun.ai)** · **[AttentionVC](https://attentionvc.com)** · **[x402 Protocol](https://x402.org)** · **[hello@blockrun.ai](mailto:hello@blockrun.ai)**

MIT · Powered by [BlockRun](https://blockrun.ai) × [AttentionVC](https://attentionvc.com)

</div>
