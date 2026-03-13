---
name: blockrun
user-invocable: true
description: Use when user needs capabilities Claude lacks (image generation, real-time X/Twitter data) or explicitly requests external models ("blockrun", "use grok", "use gpt", "dall-e", "deepseek"). For Antigravity users, also use when credits are exhausted, stuck in refactoring loops, or need a second opinion on Gemini's code.
allowed-tools: Read, Bash(python:*), Bash(python3:*), Bash(pip:*), Bash(source:*)
---

# BlockRun

**BlockRun works with Claude Code and Google Antigravity.**

You can't generate images. You have no real-time X/Twitter access. BlockRun gives you these capabilities.

## CRITICAL: Use the SDK, NOT MCP Tools

**NEVER use `blockrun_twitter`, `blockrun_chat`, `blockrun_image`, or any MCP tools for BlockRun operations.**

Always use the `blockrun_llm` Python SDK via Bash. The MCP tools are for simple demos only. The SDK gives you structured data, pagination, CSV export, and proper error handling.

**Wrong:** `blockrun_twitter(query: "@username")` — unstructured, no pagination, wastes money
**Right:** `client.x_followings("username")` — structured data, pagination, export-ready

## Quick Decision Tree

When the user asks for something, find the matching row and run the code. Do NOT explore, do NOT fetch GitHub docs, do NOT inspect signatures. Just run it.

| User Wants | Method | Cost | Code Section |
|------------|--------|------|--------------|
| X/Twitter followings list | `client.x_followings(username)` | $0.05/page | [Bulk Followings Export](#bulk-followings-export-to-csv) |
| X/Twitter followers list | `client.x_followers(username)` | $0.05/page | [Bulk Followers Export](#bulk-followers-export-to-csv) |
| X/Twitter user profile | `client.x_user_lookup([usernames])` | $0.02 | [User Lookup](#x-user-lookup) |
| X/Twitter user info (single) | `client.x_user_info(username)` | $0.002 | [User Info](#x-user-info) |
| X/Twitter verified followers | `client.x_verified_followers(user_id)` | $0.048/page | — |
| User's tweets | `client.x_user_tweets(username)` | $0.032/page | [User Tweets](#x-user-tweets) |
| Tweets mentioning user | `client.x_user_mentions(username)` | $0.032/page | — |
| Batch tweet lookup | `client.x_tweet_lookup(tweet_ids)` | $0.16/batch | — |
| Tweet replies | `client.x_tweet_replies(tweet_id)` | $0.032/page | — |
| Tweet thread | `client.x_tweet_thread(tweet_id)` | $0.032/page | — |
| X/Twitter search | `client.x_search(query)` | $0.032/page | [X Search](#x-search) |
| Trending topics | `client.x_trending()` | $0.002 | [Trending Topics](#x-trending-topics) |
| Rising/viral articles | `client.x_articles_rising()` | $0.05 | — |
| Author analytics | `client.x_author_analytics(handle)` | $0.02 | [Author Analytics](#x-author-analytics) |
| Compare two authors | `client.x_compare_authors(handle1, handle2)` | $0.05 | — |
| Real-time X/Twitter posts | `client.chat("xai/grok-3", prompt, search=True)` | ~$0.25 | [Live Search](#real-time-xtwitter-search) |
| Web/news search | `client.search(query)` | ~$0.25 | [Standalone Search](#standalone-search) |
| Image generation | `client.generate(prompt)` | $0.01-$0.04 | [Image Generation](#image-generation) |
| Image editing | `client.image_edit(prompt, image)` | $0.02-$0.04 | [Image Editing](#image-editing) |
| LLM chat (GPT, DeepSeek, etc) | `client.chat(model, prompt)` | varies | [Basic Chat](#basic-chat) |
| Check balance | `client.get_balance()` | free | [Wallet & Balance](#wallet--balance) |

## Execution Flow (Every Time)

**Always run as ONE Python script.** Do not split into multiple calls.

```
1. Check chain preference (~/.blockrun/.chain) → "base" or "solana"
   - If no preference file exists, ask user: "Base (USDC on Base) or Solana (USDC on Solana)?"
   - Save their choice to ~/.blockrun/.chain
2. Create client (setup_agent_wallet for Base, setup_agent_solana_wallet for Solana)
3. Check balance
4. Estimate cost, show to user, ask to proceed
5. If confirmed: execute, show results, show cost
```

### Chain Selection Helper
```python
from pathlib import Path

chain_file = Path.home() / ".blockrun" / ".chain"
chain = chain_file.read_text().strip() if chain_file.exists() else None

if chain == "solana":
    from blockrun_llm import setup_agent_solana_wallet
    client = setup_agent_solana_wallet()
else:
    from blockrun_llm import setup_agent_wallet
    client = setup_agent_wallet()
```

If user wants to switch chains: `echo "solana" > ~/.blockrun/.chain` (or `"base"`).

## How to Invoke

Users can trigger this skill in two ways:
- **Slash command:** `/blockrun <request>` (e.g., `/blockrun use grok to analyze @elonmusk`)
- **Keyword in message:** Include "blockrun" or model names (e.g., "blockrun grok find trending crypto", "use grok to check...")

Common triggers: `blockrun`, `use grok`, `use gpt`, `dall-e`, `deepseek`, `generate image`, `following`, `followers`, `x.com`, `twitter`, `trending`, `tweets`, `mentions`, `thread`

## CRITICAL: Balance Check Before API Calls

**You MUST check wallet balance and get user confirmation BEFORE making any paid API call.**

### Step 1: Check Balance First
```python
from pathlib import Path

chain_file = Path.home() / ".blockrun" / ".chain"
chain = chain_file.read_text().strip() if chain_file.exists() else "base"

if chain == "solana":
    from blockrun_llm import setup_agent_solana_wallet, get_solana_usdc_balance
    client = setup_agent_solana_wallet()
    address = client.get_wallet_address()
    balance = get_solana_usdc_balance(address)
else:
    from blockrun_llm import setup_agent_wallet
    client = setup_agent_wallet()
    balance = client.get_balance()
    address = client.get_wallet_address()
```

### Step 2: Estimate Cost & Ask User
Before calling any model, show the user:
```
Wallet Status
   Address: 0x413c...1DC3
   Balance: $0.39 USDC

Estimated Cost
   Grok + Live Search (10 sources): ~$0.25

Proceed? (Balance after: ~$0.14)
```

Wait for user confirmation before making the API call.

### Step 3: Handle Insufficient Balance
If balance is too low, show a friendly message:
```
Insufficient balance for this operation.

Current: $0.05 USDC
Required: ~$0.25 (Grok + Live Search)

To fund your wallet, send USDC on Base to:
0x413c7846194698829F8605C631c06c91B7B71DC3

Would you like to:
1. Use fewer search sources (~$0.13 for 5 sources)
2. Try a cheaper model (DeepSeek ~$0.001)
```

### Cost Reference for Confirmation
| Operation | Estimated Cost |
|-----------|---------------|
| Grok + Live Search (10 sources) | ~$0.25 |
| Grok + Live Search (5 sources) | ~$0.13 |
| Standalone search (10 sources) | ~$0.25 |
| X user lookup (1-10 users) | $0.02 |
| X user info (single) | $0.002 |
| X followers/followings (1 page ~200 accounts) | $0.05 |
| X followers/followings (1000 accounts, ~5 pages) | ~$0.25 |
| X verified followers (1 page) | $0.048 |
| X user tweets / mentions (1 page) | $0.032 |
| X tweet lookup (batch) | $0.16 |
| X tweet replies / thread (1 page) | $0.032 |
| X search (1 page) | $0.032 |
| X trending topics | $0.002 |
| X rising/viral articles | $0.05 |
| X author analytics | $0.02 |
| X compare authors | $0.05 |
| GPT-5.2 query (typical) | ~$0.02 |
| DeepSeek query | ~$0.001 |
| DALL-E image | $0.04 |
| Image editing (img2img) | $0.02-0.04 |

## Output Guidelines

**Keep it clean.** The user wants results, not process.

- **Hide retries** - If an API call fails and you retry, don't show the error. Just retry silently and show the final result.
- **No stack traces** - If something fails, summarize the error in one sentence. Don't dump tracebacks.
- **Concise results** - For balance checks: just show wallet address and balance. For X/Twitter: summarize the findings, don't show raw API responses.
- **Show cost at the end** - After BlockRun operations, show what was spent: `Cost: $0.28`

---

## Complete Copy-Paste Scripts

### Bulk Followings Export to CSV

When user asks "get followings for @username" or "export following list to CSV":

```python
from blockrun_llm import setup_agent_wallet
import csv, os

client = setup_agent_wallet()
username = "bc1beat"  # CHANGE THIS

# Paginate all followings
all_followings = []
cursor = None
while True:
    result = client.x_followings(username, cursor=cursor)
    all_followings.extend(result.followings)
    print(f"Fetched {len(all_followings)} followings so far...")
    if not result.has_next_page:
        break
    cursor = result.next_cursor

# Write CSV
outfile = os.path.expanduser(f"~/Desktop/{username}_followings.csv")
with open(outfile, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["screen_name", "name", "followers", "following", "verified", "description"])
    for u in all_followings:
        writer.writerow([
            getattr(u, "screen_name", ""),
            getattr(u, "name", ""),
            getattr(u, "followers_count", ""),
            getattr(u, "following_count", ""),
            getattr(u, "is_blue_verified", ""),
            getattr(u, "description", "").replace("\n", " ")[:100],
        ])

print(f"\nDone! {len(all_followings)} followings saved to {outfile}")
spending = client.get_spending()
print(f"Cost: ${spending['total_usd']:.4f}")
client.close()
```

### Bulk Followers Export to CSV

When user asks "get followers for @username" or "export follower list":

```python
from blockrun_llm import setup_agent_wallet
import csv, os

client = setup_agent_wallet()
username = "blockrunai"  # CHANGE THIS

# Paginate all followers
all_followers = []
cursor = None
while True:
    result = client.x_followers(username, cursor=cursor)
    all_followers.extend(result.followers)
    print(f"Fetched {len(all_followers)} followers so far...")
    if not result.has_next_page:
        break
    cursor = result.next_cursor

# Write CSV
outfile = os.path.expanduser(f"~/Desktop/{username}_followers.csv")
with open(outfile, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["screen_name", "name", "followers", "following", "verified", "description"])
    for u in all_followers:
        writer.writerow([
            getattr(u, "screen_name", ""),
            getattr(u, "name", ""),
            getattr(u, "followers_count", ""),
            getattr(u, "following_count", ""),
            getattr(u, "is_blue_verified", ""),
            getattr(u, "description", "").replace("\n", " ")[:100],
        ])

print(f"\nDone! {len(all_followers)} followers saved to {outfile}")
spending = client.get_spending()
print(f"Cost: ${spending['total_usd']:.4f}")
client.close()
```

### X User Lookup

When user asks "look up @username profile" or "who is @username":

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
users = client.x_user_lookup(["elonmusk", "blockrunai"])  # CHANGE THESE
for u in users.users:
    print(f"@{u.userName}: {u.followers} followers, verified={u.isBlueVerified}")
    print(f"  Bio: {u.description[:100]}")

spending = client.get_spending()
print(f"\nCost: ${spending['total_usd']:.4f}")
client.close()
```

### X User Info

When user asks "get info on @username" (single user, cheaper than x_user_lookup):

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
info = client.x_user_info("elonmusk")  # CHANGE THIS
d = info.data  # Raw dict from AttentionVC
print(f"@{d.get('userName', '')}: {d.get('followers', 0)} followers")
print(f"Bio: {str(d.get('description', ''))[:100]}")

spending = client.get_spending()
print(f"\nCost: ${spending['total_usd']:.4f}")
client.close()
```

### X User Tweets

When user asks "show recent tweets from @username" or "what has @username posted":

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
result = client.x_user_tweets("blockrunai")  # CHANGE THIS
for tweet in result.tweets:
    print(f"- {(tweet.text or '')[:120]}")
    print(f"  Likes: {tweet.favorite_count or 0} | RTs: {tweet.retweet_count or 0}")

spending = client.get_spending()
print(f"\nCost: ${spending['total_usd']:.4f}")
client.close()
```

### X Search

When user asks "search X for ..." or "find tweets about ...":

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
result = client.x_search("AI agents crypto")  # CHANGE THIS
for tweet in result.tweets:
    author = tweet.author or {}
    print(f"@{author.get('userName', '?')}: {(tweet.text or '')[:120]}")

spending = client.get_spending()
print(f"\nCost: ${spending['total_usd']:.4f}")
client.close()
```

### X Trending Topics

When user asks "what's trending on X" or "show trending topics":

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
result = client.x_trending()
trends = result.data.get("trends", [])
for topic in trends:
    name = topic.get("name", "") if isinstance(topic, dict) else str(topic)
    volume = topic.get("tweet_volume", "N/A") if isinstance(topic, dict) else "N/A"
    print(f"- {name} ({volume} tweets)")

spending = client.get_spending()
print(f"\nCost: ${spending['total_usd']:.4f}")
client.close()
```

### X Author Analytics

When user asks "analyze @username's X account" or "author stats for @username":

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
result = client.x_author_analytics("blockrunai")  # CHANGE THIS
d = result.data  # Raw dict from AttentionVC
print(f"Analytics for @{result.handle}:")
print(f"  Score: {d.get('score', 'N/A')}")
print(f"  Categories: {d.get('categories', [])}")

spending = client.get_spending()
print(f"\nCost: ${spending['total_usd']:.4f}")
client.close()
```

---

## Philosophy

You have a wallet. When you need a capability you lack, you pay for it autonomously.

| You Need | You Call | Pricing |
|----------|----------|---------|
| Image generation | DALL-E | $0.04/image |
| Image editing (img2img) | `client.image_edit()` | $0.02-0.04/image |
| Real-time X data | Grok + Live Search | $0.025/source |
| X user profiles | `client.x_user_lookup()` | $0.002/user (min $0.02) |
| X single user info | `client.x_user_info()` | $0.002 |
| X followers/followings | `client.x_followers()` / `x_followings()` | $0.05/page |
| X verified followers | `client.x_verified_followers()` | $0.048/page |
| X user tweets/mentions | `client.x_user_tweets()` / `x_user_mentions()` | $0.032/page |
| X tweet lookup/replies/thread | `client.x_tweet_lookup()` / `x_tweet_replies()` / `x_tweet_thread()` | $0.032-0.16 |
| X search | `client.x_search()` | $0.032/page |
| X trending topics | `client.x_trending()` | $0.002 |
| X rising articles | `client.x_articles_rising()` | $0.05 |
| X author analytics | `client.x_author_analytics()` / `x_compare_authors()` | $0.02-0.05 |
| Web + X + news search | `client.search()` | ~$0.25 (10 sources) |
| Second opinion | GPT-5.2 | $1.75/M input, $14/M output |
| Cheaper processing | DeepSeek | $0.28/M input, $0.42/M output |

**How it works:** BlockRun uses x402 micropayments to route your requests to OpenAI, xAI, Google, AttentionVC, and other providers. No API keys needed - your wallet pays per request.

**Chains supported:** Base (default via `LLMClient`) and Solana (via `SolanaLLMClient` — `pip install blockrun-llm[solana]`). All endpoints work on both chains.

## Budget Control (Optional)

If the user specifies a budget (e.g., "use at most $1"), track spending and stop when budget is reached:

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
budget = 1.0  # User's budget

# Before each call, check if within budget
spending = client.get_spending()
if spending['total_usd'] >= budget:
    print(f"Budget reached: ${spending['total_usd']:.4f} spent")
    # Stop making calls
else:
    response = client.chat("openai/gpt-5.2", "Hello!")

# At the end, report spending
spending = client.get_spending()
print(f"Total spent: ${spending['total_usd']:.4f} across {spending['calls']} calls")
```

## When to Use

| Trigger | Your Action |
|---------|-------------|
| User explicitly requests ("blockrun second opinion with GPT on...", "use grok to check...", "generate image with dall-e") | Execute via BlockRun |
| User needs something you can't do (images, live X data) | Suggest BlockRun, wait for confirmation |
| You can handle the task fine | Do it yourself, don't mention BlockRun |

### Antigravity-Specific Triggers

| Trigger | Your Action |
|---------|-------------|
| Antigravity credits exhausted / rate limited | Suggest BlockRun to continue working with DeepSeek or GPT |
| Gemini stuck in refactoring loop (repeated edits, no progress) | Call GPT or Claude via BlockRun to break the cycle |
| User wants code review on Gemini's output | Call GPT or Claude for a second opinion |
| Complex build failing with Gemini | Suggest external model review before continuing |

## Example User Prompts

| User Says | What You Do |
|-----------|-------------|
| "blockrun generate an image of a sunset" | Call DALL-E via ImageClient |
| "blockrun edit this image to add a rainbow" | Call `client.image_edit()` |
| "use grok to check what's trending on X" | Call `client.x_trending()` ($0.002, cheapest) or Grok with `search=True` |
| "blockrun lookup @elonmusk on X" | Call `client.x_user_lookup()` (cheaper than Grok) |
| "blockrun get info on @username" | Call `client.x_user_info()` for single user ($0.002) |
| "blockrun get followers of @blockrunai" | Call `client.x_followers()` with pagination |
| "get verified followers of @username" | Call `client.x_verified_followers()` |
| "find @username following" / "get following list" | Call `client.x_followings()` with pagination, export CSV |
| "show recent tweets from @username" | Call `client.x_user_tweets()` |
| "who's mentioning @username on X" | Call `client.x_user_mentions()` |
| "get replies to this tweet" | Call `client.x_tweet_replies(tweet_id)` |
| "show the full thread for this tweet" | Call `client.x_tweet_thread(tweet_id)` |
| "search X for AI agents" | Call `client.x_search()` ($0.032, cheaper than Grok search) |
| "what's trending on X right now" | Call `client.x_trending()` ($0.002) |
| "show viral articles on X" | Call `client.x_articles_rising()` |
| "analyze @username's X account" | Call `client.x_author_analytics()` |
| "compare @user1 and @user2 on X" | Call `client.x_compare_authors()` |
| "blockrun search latest AI news" | Call `client.search()` |
| "blockrun GPT review this code" | Call GPT-5.2 via LLMClient |
| "what's the latest news about AI agents?" | Suggest search or Grok (you lack real-time data) |
| "generate a logo for my startup" | Suggest DALL-E (you can't generate images) |
| "blockrun check my balance" | Show wallet balance via `get_balance()` |
| "blockrun deepseek summarize this file" | Call DeepSeek for cost savings |

### Antigravity User Prompts

| User Says | What You Do |
|-----------|-------------|
| "I ran out of Antigravity credits" | Suggest BlockRun: "Your BlockRun wallet can keep you working. Want me to route this task through DeepSeek?" |
| "Gemini keeps refactoring in circles" | Call GPT/Claude: "Let me get a fresh perspective from GPT to break this loop." |
| "Review what Gemini just did" | Call GPT/Claude for second opinion on the code |
| "This complex refactor isn't working with Gemini" | Suggest external review: "GPT might catch edge cases Gemini missed." |

## Wallet & Balance

Use `setup_agent_wallet()` to auto-create a wallet and get a client. This shows the QR code and welcome message on first use.

**Initialize client (always start with this):**
```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()  # Auto-creates wallet, shows QR if new
```

**Check balance (when user asks "show balance", "check wallet", etc.):**
```python
balance = client.get_balance()  # On-chain USDC balance
print(f"Balance: ${balance:.2f} USDC")
print(f"Wallet: {client.get_wallet_address()}")
```

**Show QR code for funding:**
```python
from blockrun_llm import generate_wallet_qr_ascii, get_wallet_address

# ASCII QR for terminal display
print(generate_wallet_qr_ascii(get_wallet_address()))
```

## SDK Usage

**Prerequisite:** Install the SDK with `pip install blockrun-llm`

### Basic Chat
```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()  # Auto-creates wallet if needed
response = client.chat("openai/gpt-5.2", "What is 2+2?")
print(response)

# Check spending
spending = client.get_spending()
print(f"Spent ${spending['total_usd']:.4f}")
```

### Real-time X/Twitter Search

**IMPORTANT:** For real-time X/Twitter data, you MUST enable Live Search with `search=True` or `search_parameters`.

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()

# Simple: Enable live search with search=True
response = client.chat(
    "xai/grok-3",
    "What are the latest posts from @blockrunai on X?",
    search=True  # Enables real-time X/Twitter search
)
print(response)
```

### Advanced X Search with Filters

```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()

response = client.chat(
    "xai/grok-3",
    "Analyze @blockrunai's recent content and engagement",
    search_parameters={
        "mode": "on",
        "sources": [
            {
                "type": "x",
                "included_x_handles": ["blockrunai"],
                "post_favorite_count": 5
            }
        ],
        "max_search_results": 20,
        "return_citations": True
    }
)
print(response)
```

### Image Generation
```python
from blockrun_llm import ImageClient

client = ImageClient()
result = client.generate("A cute cat wearing a space helmet")
print(result.data[0].url)
```

### Image Editing
```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
result = client.image_edit(
    prompt="Make the sky purple and add northern lights",
    image="data:image/png;base64,...",  # base64 or URL
)
print(result.data[0].url)
```

### Standalone Search
```python
from blockrun_llm import setup_agent_wallet

client = setup_agent_wallet()
result = client.search("latest AI agent frameworks 2026")
print(result.summary)
for cite in result.citations or []:
    print(f"  - {cite}")
```

## xAI Live Search Reference

Live Search is xAI's real-time data API. Cost: **$0.025 per source** (default 10 sources = ~$0.26).

To reduce costs, set `max_search_results` to a lower value:
```python
# Only use 5 sources (~$0.13)
response = client.chat("xai/grok-3", "What's trending?",
    search_parameters={"mode": "on", "max_search_results": 5})
```

### Search Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `mode` | string | "auto" | "off", "auto", or "on" |
| `sources` | array | web,news,x | Data sources to query |
| `return_citations` | bool | true | Include source URLs |
| `from_date` | string | - | Start date (YYYY-MM-DD) |
| `to_date` | string | - | End date (YYYY-MM-DD) |
| `max_search_results` | int | 10 | Max sources to return (customize to control cost) |

### Source Types

**X/Twitter Source:**
```python
{
    "type": "x",
    "included_x_handles": ["handle1", "handle2"],  # Max 10
    "excluded_x_handles": ["spam_account"],        # Max 10
    "post_favorite_count": 100,  # Min likes threshold
    "post_view_count": 1000      # Min views threshold
}
```

**Web Source:**
```python
{
    "type": "web",
    "country": "US",  # ISO alpha-2 code
    "allowed_websites": ["example.com"],  # Max 5
    "safe_search": True
}
```

**News Source:**
```python
{
    "type": "news",
    "country": "US",
    "excluded_websites": ["tabloid.com"]  # Max 5
}
```

## Available Models

### Capabilities Claude Lacks (Primary Use)

| Model / Endpoint | Capability | Cost |
|------------------|------------|------|
| `openai/dall-e-3` | Image generation (photorealistic) | $0.04/image |
| `google/nano-banana` | Image generation (fast, artistic) | $0.01/image |
| `client.image_edit()` | Image editing (img2img) | $0.02-0.04/image |
| `client.x_user_lookup()` | X/Twitter user profiles | $0.002/user (min $0.02) |
| `client.x_user_info()` | X/Twitter single user info | $0.002 |
| `client.x_verified_followers()` | X/Twitter verified followers | $0.048/page |
| `client.x_followers()` | X/Twitter followers | $0.05/page (~200) |
| `client.x_followings()` | X/Twitter followings | $0.05/page (~200) |
| `client.x_user_tweets()` | User's tweets | $0.032/page |
| `client.x_user_mentions()` | Tweets mentioning user | $0.032/page |
| `client.x_tweet_lookup()` | Batch tweet lookup | $0.16/batch |
| `client.x_tweet_replies()` | Tweet replies | $0.032/page |
| `client.x_tweet_thread()` | Tweet thread | $0.032/page |
| `client.x_search()` | X/Twitter search | $0.032/page |
| `client.x_trending()` | Trending topics | $0.002 |
| `client.x_articles_rising()` | Rising/viral articles | $0.05 |
| `client.x_author_analytics()` | Author analytics | $0.02 |
| `client.x_compare_authors()` | Compare two authors | $0.05 |
| `xai/grok-3` + search | Live X/Twitter posts & trends | ~$0.25 (10 sources) |
| `client.search()` | Web + X + news search | ~$0.25 (10 sources) |

### LLM Models (Second Opinions & Bulk Processing)

| Model | Best For | Pricing |
|-------|----------|---------|
| `openai/gpt-5.2` | Second opinions, code review | $1.75/M in, $14/M out |
| `deepseek/deepseek-chat` | Bulk processing (cheapest) | $0.28/M in, $0.42/M out |
| `openai/gpt-5-mini` | Cost-optimized reasoning | $0.30/M in, $1.20/M out |
| `openai/o4-mini` | Efficient reasoning | $1.10/M in, $4.40/M out |
| `openai/o3` | Complex reasoning | $10/M in, $40/M out |
| `google/gemini-2.5-flash` | Very long documents | $0.15/M in, $0.60/M out |

*M = million tokens. Actual cost depends on your prompt and response length.*

## Cost Reference

All LLM costs are per million tokens (M = 1,000,000 tokens).

| Model | Input | Output |
|-------|-------|--------|
| GPT-5.2 | $1.75/M | $14.00/M |
| GPT-5-mini | $0.30/M | $1.20/M |
| Grok-3 (no search) | $3.00/M | $15.00/M |
| DeepSeek | $0.28/M | $0.42/M |

| Fixed Cost Actions | |
|-------|--------|
| Grok Live Search | $0.025/source (default 10 = $0.25) |
| Standalone search | $0.025/source (default 10 = $0.25) |
| X user lookup | $0.002/user (min $0.02) |
| X user info (single) | $0.002 |
| X verified followers | $0.048/page |
| X followers/followings | $0.05/page (~200 accounts) |
| X user tweets / mentions | $0.032/page |
| X tweet lookup (batch) | $0.16/batch |
| X tweet replies / thread | $0.032/page |
| X search | $0.032/page |
| X trending topics | $0.002 |
| X rising/viral articles | $0.05 |
| X author analytics | $0.02 |
| X compare authors | $0.05 |
| DALL-E image | $0.04/image |
| Image editing (img2img) | $0.02-0.04/image |
| Nano Banana image | $0.01/image |

**Typical costs:** A 500-word prompt (~750 tokens) to GPT-5.2 costs ~$0.001 input. A 1000-word response (~1500 tokens) costs ~$0.02 output.

## Setup & Funding

**Wallet location:** `$HOME/.blockrun/.session` (e.g., `/Users/username/.blockrun/.session`)

**First-time setup:**
1. Wallet auto-creates when `setup_agent_wallet()` is called
2. Check wallet and balance:
```python
from blockrun_llm import setup_agent_wallet
client = setup_agent_wallet()
print(f"Wallet: {client.get_wallet_address()}")
print(f"Balance: ${client.get_balance():.2f} USDC")
```
3. Fund wallet with $1-5 USDC on Base network

**Show QR code for funding (ASCII for terminal):**
```python
from blockrun_llm import generate_wallet_qr_ascii, get_wallet_address
print(generate_wallet_qr_ascii(get_wallet_address()))
```

## Solana Wallet Management

BlockRun also supports Solana for USDC payments. Install Solana support: `pip install blockrun-llm[solana]`

**Solana wallet location:** `$HOME/.blockrun/.solana-session`

### Create Solana Wallet
```python
from blockrun_llm import setup_agent_solana_wallet

client = setup_agent_solana_wallet()  # Auto-creates wallet, returns SolanaLLMClient
```

### Check Solana Balance
```python
from blockrun_llm import get_or_create_solana_wallet, get_solana_usdc_balance

wallet = get_or_create_solana_wallet()
balance = get_solana_usdc_balance(wallet["address"])
print(f"Balance: ${balance:.2f} USDC")
print(f"Wallet: {wallet['address']}")
```

### Fund Solana Wallet (QR Code)
```python
from blockrun_llm import generate_solana_qr_ascii, get_or_create_solana_wallet

wallet = get_or_create_solana_wallet()
print(generate_solana_qr_ascii(wallet["address"]))
```

### Using SolanaLLMClient
```python
from blockrun_llm import setup_agent_solana_wallet

client = setup_agent_solana_wallet()
response = client.chat("openai/gpt-5.2", "Hello!")
print(response)
```

### When to Use Base vs Solana

| Use Case | Chain | Client |
|----------|-------|--------|
| Default payments | Base | `LLMClient` via `setup_agent_wallet()` |
| Solana-native users | Solana | `SolanaLLMClient` via `setup_agent_solana_wallet()` |
| Already have USDC on Solana | Solana | `SolanaLLMClient` |
| Already have USDC on Base | Base | `LLMClient` |

Both chains access the same models and endpoints. Choose based on where the user's USDC is.

## Troubleshooting

**PaymentError: Payment was rejected**
-> NEVER show raw stack traces. Always check balance first (see "CRITICAL: Balance Check" section above).
If you get this error, show a user-friendly message:
```
Payment failed - insufficient balance.

Current balance: $0.05 USDC
Wallet: 0x413c7846194698829F8605C631c06c91B7B71DC3

Options:
1. Fund wallet with USDC on Base network
2. Use fewer search sources to reduce cost
3. Try a cheaper model (DeepSeek)
```

**"Grok says it has no real-time access"**
-> You forgot to enable Live Search. Add `search=True`:
```python
response = client.chat("xai/grok-3", "What's trending?", search=True)
```

**Module not found**
-> Install the SDK: `pip install blockrun-llm`

## Error Handling Pattern

Always wrap API calls with balance checking:
```python
from blockrun_llm import setup_agent_wallet
from blockrun_llm.types import PaymentError

client = setup_agent_wallet()
balance = client.get_balance()
estimated_cost = 0.25  # Grok + Live Search

# Pre-flight check
if balance < estimated_cost:
    print(f"Insufficient balance: ${balance:.2f} USDC")
    print(f"Required: ~${estimated_cost:.2f}")
    print(f"Wallet: {client.get_wallet_address()}")
    # Ask user what to do
else:
    # User confirmed, make the call
    try:
        response = client.chat("xai/grok-3", "Query", search=True)
        print(response)
        print(f"\nCost: ${client.get_spending()['total_usd']:.2f}")
    except PaymentError:
        print("Payment failed. Balance may have changed.")
```

## Updates

```bash
pip install --upgrade blockrun-llm
```
