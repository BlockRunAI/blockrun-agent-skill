# SocialClaw — X/Twitter Marketing Intelligence Agent

<div align="center">

![SocialClaw](assets/blockrun-agent-skill.png)

[![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-orange.svg)](https://github.com/anthropics/skills)
[![No API Keys](https://img.shields.io/badge/API_Keys-None_Required-brightgreen.svg)](https://blockrun.ai)
[![USDC Payments](https://img.shields.io/badge/Pay_with-USDC-2775CA.svg)](https://blockrun.ai)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**X/Twitter intelligence for growth. No API keys, no subscriptions — just USDC micropayments.**

</div>

---

## 7 Marketing Workflows

SocialClaw chains multiple X/Twitter API calls into actionable marketing intelligence. One wallet, one command.

---

### 1. Insight — Account Deep-Dive

_Who is this account? What's their influence? Who talks about them?_

```
socialclaw insight @jessepollak
```

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

**What you get:** Profile stats, F/F ratio, engagement quality, top followers ranked by influence, mention sentiment.

---

### 2. Radar — Topic Intelligence

_What's hot? What content is working? Where should I jump in?_

```
socialclaw radar "AI agents"
```

```
  TRENDING NOW
    Anthropic          158 articles   115,983,616 views
    OpenAI              48 articles    51,378,182 views
    Claude Code         29 articles    44,825,583 views

  LATEST TWEETS (20 found)
    @Computerworld  [0 likes] Microsoft shuffles leadership as Copilot and AI agents...
    @badlogicgames  [5 likes] pi now has feature parity with other agents from July 2025...

  RISING ARTICLES
    [viral] One day — https://x.com/Tad_2/status/...

  TOPIC PULSE
    Avg likes per tweet: 0.5

  Cost: $0.07 (4 calls)
```

**What you get:** Trending topics with view counts, latest conversation, top-performing tweets, viral content detection, content opportunity signals.

---

### 3. Compare — Competitor Analysis

_Side-by-side: who's winning and why?_

```
socialclaw compare @jessepollak @VitalikButerin
```

```
  METRIC              @jessepollak    @VitalikButerin
  ─────────────────────────────────────────────────
  Followers              347,004         5,800,000
  Following                4,406            ~3,000
  Tweets                  57,569           ~15,000
  Verified                   Yes               Yes
  F/F Ratio               78.7x            ~1900x

  MENTIONS              @jessepollak    @VitalikButerin
  ─────────────────────────────────────────────────
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

**What you get:** Follower counts, posting frequency, engagement comparison, audience quality, who has momentum.

---

### 4. Audience — Follower Segmentation

_Who follows them? Cluster by influence tier._

```
socialclaw audience @jessepollak
```

Gets 200 followers → batch lookups top 50 → segments into tiers:

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

**What you get:** Audience tiers, common interests from bios, potential partnership targets.

---

### 5. Scout — KOL Discovery

_Find the key voices in any topic._

```
socialclaw scout "base blockchain"
```

Searches topic → extracts authors → batch lookups → ranks by influence:

```
  TOP VOICES ON "base blockchain"
    @jessepollak            347,004 followers — @base builder #001
    @BuildOnBase             89,200 followers — Official Base account
    @coinaborsh              45,000 followers — Base ecosystem analyst
    @web3marketer            23,400 followers — Growth at Base projects
    ...

  Cost: $0.07 (2 calls)
```

**What you get:** Ranked influencer list with follower counts and bios — ready for outreach.

---

### 6. Hitlist — Engagement Targets

_High-value conversations to engage with RIGHT NOW._

```
socialclaw hitlist "AI agents crypto"
```

Finds high-engagement tweets → ranks by engagement × author influence:

```
  ENGAGEMENT TARGETS
    @solana_daily (45K followers) — 14 likes
      "Solana Projects to Watch this Week: @anagramxyz @BlockRunAI..."
      → Reply angle: share your project's update

    @A47X124 (12K followers) — 8 likes
      "The ones not on these lists are usually the ones that surprise..."
      → Reply angle: agree + mention an unlisted project

    @taowang1 (8K followers) — 4 likes
      "@MAIN_AI_DEX @CoinbaseDev @BlockRunAI Please include $fxUSD"
      → Reply angle: engage with ecosystem discussion

  Cost: $0.03 (1 call)
```

**What you get:** Ranked conversations to join, sorted by engagement potential, with suggested reply angles.

---

### 7. Brief — Daily Marketing Report

_What happened overnight? What should I post today?_

```
socialclaw brief @blockrunai
```

```
  YOUR MENTIONS (5 new)
    @KashKysh: Let's watch closely folks
    @Rich_lifee_: The are the ones that ends up with the biggest...

  TRENDING NOW
    Anthropic          158 articles   115M views
    OpenAI              48 articles    51M views

  RISING CONTENT
    "One day" — going viral
    "AI agents reshape products" — rising

  SUGGESTED ACTIONS
    1. Reply to @Rich_lifee_ — they're talking about you to 5K followers
    2. Create content around "Anthropic" trend (115M views today)
    3. Share perspective on "AI agents reshape products" article

  Cost: $0.08 (3 calls)
```

**What you get:** Morning brief with mentions, trends, and 3 concrete actions for today.

---

## Install

In Claude Code:

```
try https://github.com/BlockRunAI/socialclaw
```

Or manually:

```bash
git clone https://github.com/BlockRunAI/socialclaw
cd socialclaw
pip install blockrun-llm[solana]
python scripts/socialclaw.py insight @anyuser
```

---

## Wallet Setup

SocialClaw auto-detects wallets. No manual config needed.

It scans `~/.<any-folder>/wallet.json` and `~/.<any-folder>/solana-wallet.json` — works with any compatible wallet provider. Solana or Base, whichever has funds.

---

## Pricing

| Workflow | API Calls | Cost |
|----------|-----------|------|
| Insight | profile + mentions + followers | ~$0.08 |
| Radar | trending + search + rising articles | ~$0.07 |
| Compare | 2× profile + 2× mentions + 2× followers | ~$0.15 |
| Audience | followers + batch lookup top 50 | ~$0.15 |
| Scout | search + batch lookup authors | ~$0.07 |
| Hitlist | search (sorted by engagement) | ~$0.03 |
| Brief | mentions + trending + rising | ~$0.08 |

**$1 USDC gets you ~12 full reports.** No subscriptions, no monthly fees.

---

## API Endpoints

All data via [BlockRun](https://blockrun.ai)'s unified gateway, powered by [AttentionVC](https://attentionvc.com):

| Endpoint | What you get | Cost |
|----------|-------------|------|
| `users/info` | Profile, bio, stats, verification | $0.002 |
| `users/lookup` | Batch profiles (up to 100) | $0.002/user |
| `users/followers` | Follower list with stats (~200/page) | $0.05/page |
| `users/followings` | Following list (~200/page) | $0.05/page |
| `users/tweets` | User's tweets with engagement | $0.032/page |
| `users/mentions` | Who's talking about them | $0.032/page |
| `search` | Search tweets (Latest/Top) | $0.032/page |
| `trending` | Trending topics + view counts | $0.002 |
| `articles/rising` | Viral content detection | $0.05 |
| `tweets/lookup` | Batch tweet data (up to 200) | $0.16/batch |
| `tweets/replies` | Replies to a tweet | $0.032/page |
| `tweets/thread` | Full thread context | $0.032/page |

---

## Data Auto-Save

Every paid API response is saved to `~/.blockrun/data/` as JSON — you paid for it, you keep it.

```
~/.blockrun/data/
  20260314_030816_trending.json
  20260314_030820_search_blockrunai.json
  20260314_025259_mentions_jessepollak.json
```

---

## How It Works

```
You: "analyze @competitor's X presence"
       ↓
SocialClaw: finds wallet → calls BlockRun APIs → pays with USDC → saves data locally
       ↓
Output: actionable marketing insight report
```

- Wallet auto-detected from any `~/.<provider>/` folder
- Payment via x402 protocol (USDC on Solana or Base)
- Private key never leaves your machine — only signatures sent
- All data cached locally in `~/.blockrun/data/`

> All capabilities — X/Twitter data, image generation, LLM, and search — are available through BlockRun's unified gateway. One wallet, one SDK, everything you need.

---

## Links

[blockrun.ai](https://blockrun.ai) · [AttentionVC](https://attentionvc.com) · [x402 Protocol](https://x402.org) · [care@blockrun.ai](mailto:care@blockrun.ai)

---

MIT · Powered by [BlockRun](https://blockrun.ai) × [AttentionVC](https://attentionvc.com) · Built by [@bc1beat](https://x.com/bc1beat)
