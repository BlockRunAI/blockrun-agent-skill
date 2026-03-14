#!/usr/bin/env python3
"""
SocialClaw v3 — X/Twitter Marketing Intelligence

Structured BlockRun APIs first, Grok AI for enhancement. All via x402 micropayments.

Data layer:
  - Structured APIs (primary): trending, user info, search, mentions, followers
  - Grok Live Search (enhancement): AI-powered analysis, fallback on 502s

Workflows:
  1. insight @username     — deep-dive account analysis
  2. radar <topic>         — trending topics + content opportunities
  3. compare @a @b         — side-by-side competitor analysis
  4. engage @username      — find mentions & generate reply drafts
  5. check @username       — verify posted tweets & engagement
  6. search <query>        — structured search + top tweets
  7. tweet <id_or_url>     — look up specific tweet + replies
  8. thread <id_or_url>    — get full tweet thread
  9. analytics @handle     — author intelligence report
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# Auto-install dependencies if missing
def _ensure_deps():
    try:
        import blockrun_llm  # noqa: F401
    except ImportError:
        print("  Installing blockrun-llm[solana]...")
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q", "blockrun-llm[solana]>=0.8.0"],
            stdout=subprocess.DEVNULL,
        )

_ensure_deps()

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from scripts.utils.config import get_chain, get_wallet_source, get_private_key
except ImportError:
    from utils.config import get_chain, get_wallet_source, get_private_key


def _get_client():
    """Get a client using any available wallet (Solana or Base)."""
    from blockrun_llm.solana_wallet import load_solana_wallet
    from blockrun_llm.wallet import load_wallet

    sol_key = load_solana_wallet()
    if sol_key:
        from blockrun_llm import SolanaLLMClient
        client = SolanaLLMClient(private_key=sol_key)
        chain = "solana"
    else:
        base_key = load_wallet()
        if not base_key:
            print("  Error: No wallet found.")
            print("  Place wallet.json or solana-wallet.json in any ~/.<provider>/ folder.")
            sys.exit(1)
        from blockrun_llm import LLMClient
        client = LLMClient(private_key=base_key)
        chain = "base"

    addr = client.get_wallet_address()
    print(f"  Wallet: {addr[:6]}...{addr[-4:]} ({chain})")
    print(f"  Balance: ${client.get_balance():.2f}")
    return client


DATA_DIR = os.path.expanduser("~/.blockrun/data")


def _save_local(endpoint: str, body: dict, result):
    """Save every paid API response locally — you paid for it, keep it."""
    os.makedirs(DATA_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = endpoint.strip("/").replace("v1/x/", "").replace("v1/", "").replace("/", "_")

    ctx = ""
    if isinstance(body, dict):
        ctx = body.get("username") or body.get("query") or body.get("handle") or ""
    ctx = str(ctx).replace(" ", "-").replace("@", "")[:30]
    if ctx:
        slug = f"{slug}_{ctx}"

    filename = f"{ts}_{slug}.json"
    filepath = os.path.join(DATA_DIR, filename)

    save_data = result if isinstance(result, dict) else {"text": str(result)}
    with open(filepath, "w") as f:
        json.dump({"endpoint": endpoint, "request": body, "response": save_data,
                    "timestamp": ts}, f, indent=2, ensure_ascii=False)
    return filepath


# ── Data Layer ─────────────────────────────────────────────────

def _api(client, endpoint: str, body: dict) -> Dict[str, Any]:
    """Make a paid structured API call with retry on 502."""
    try:
        result = client._request_with_payment_raw(endpoint, body)
    except Exception as e:
        if "502" in str(e):
            import time
            time.sleep(2)
            try:
                result = client._request_with_payment_raw(endpoint, body)
            except Exception:
                return {}  # Return empty — caller should fallback to Grok
        else:
            raise

    _save_local(endpoint, body, result)
    return result


def _grok_search(client, query: str, *, x_only: bool = True,
                 min_likes: int = 0, max_results: int = 10,
                 system: str = None, from_date: str = None) -> str:
    """
    Search X/Twitter via Grok Live Search.
    Reliable fallback when /v1/x/search 502s.
    Returns Grok's natural language analysis with citations.
    """
    sources = []
    if x_only:
        x_source = {"type": "x"}
        if min_likes > 0:
            x_source["post_favorite_count"] = min_likes
        sources.append(x_source)
    else:
        sources.append({"type": "x"})
        sources.append({"type": "web"})

    search_params = {
        "mode": "on",
        "sources": sources,
        "return_citations": True,
        "max_search_results": max_results,
    }
    if from_date:
        search_params["from_date"] = from_date

    default_system = (
        "You are a Twitter/X data analyst. "
        "For every tweet you mention, ALWAYS include the direct URL (https://x.com/username/status/id). "
        "Include engagement metrics (likes, retweets, views) when available. "
        "Be concise and factual."
    )

    sys_msg = system or default_system
    messages = [
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": query},
    ]

    result = client.chat_completion(
        "xai/grok-3",
        messages,
        max_tokens=2048,
        search_parameters=search_params,
    )
    response = result.choices[0].message.content or ""

    _save_local("grok_search", {"query": query, "x_only": x_only}, {"text": response})
    return response


def _smart_search(client, query: str, query_type: str = "Latest") -> Dict[str, Any]:
    """
    Try structured /v1/x/search first. If 502, fallback to Grok Live Search.
    Returns structured data when possible, Grok analysis as fallback.
    """
    try:
        result = client._request_with_payment_raw(
            "/v1/x/search", {"query": query, "queryType": query_type}
        )
        _save_local("/v1/x/search", {"query": query, "queryType": query_type}, result)
        return {"source": "api", "data": result}
    except Exception as e:
        if "502" in str(e) or "500" in str(e):
            print(f"    (API 502 → switching to Grok Live Search)")
            grok_result = _grok_search(
                client, f"Find the {query_type.lower()} tweets about: {query}. "
                f"List each tweet with: author handle, text, likes, retweets, and direct URL.",
                min_likes=5 if query_type == "Top" else 0,
            )
            return {"source": "grok", "data": grok_result}
        raise


def _smart_user_tweets(client, username: str) -> Dict[str, Any]:
    """
    Get user's tweets. Try /v1/x/users/tweets first, fallback to Grok.
    """
    try:
        result = client._request_with_payment_raw(
            "/v1/x/users/tweets", {"username": username}
        )
        _save_local("/v1/x/users/tweets", {"username": username}, result)
        return {"source": "api", "data": result}
    except Exception as e:
        if "502" in str(e) or "500" in str(e):
            print(f"    (API 502 → switching to Grok Live Search)")
            grok_result = _grok_search(
                client,
                f"Show me the latest 15 tweets from @{username}. "
                f"For each tweet include: full text, like count, retweet count, "
                f"and the direct tweet URL (https://x.com/{username}/status/...).",
            )
            return {"source": "grok", "data": grok_result}
        raise


# ── Display Helpers ────────────────────────────────────────────

def _tweet_link(tw: dict) -> str:
    """Get direct link to a tweet."""
    tid = tw.get("id", "")
    author = tw.get("author", {})
    handle = author.get("userName", "")
    if tid and handle:
        return f"https://x.com/{handle}/status/{tid}"
    elif tid:
        return f"https://x.com/i/status/{tid}"
    return ""


def _print_tweet(tw: dict, indent: str = "    ", max_text: int = 100):
    """Print a tweet with author, engagement, text, and link."""
    author = tw.get("author", {})
    handle = author.get("userName", "?")
    text = tw.get("text", "")[:max_text].replace("\n", " ")
    likes = tw.get("likeCount", 0)
    rts = tw.get("retweetCount", 0)
    link = _tweet_link(tw)
    print(f"{indent}@{handle:<16} {likes:>3} likes  {rts:>3} RTs  {text}")
    if link:
        print(f"{indent}  {link}")


def _print_grok_result(result: Dict[str, Any], label: str = ""):
    """Print result from either structured API or Grok fallback."""
    if result["source"] == "api":
        tweets = result["data"].get("tweets", [])
        if label:
            print(f"\n  {label} ({len(tweets)} found)")
        for tw in tweets[:8]:
            _print_tweet(tw, max_text=110)
    else:
        if label:
            print(f"\n  {label} (via Grok Live Search)")
        print(result["data"])


# ── Workflow 1: Insight Report ──────────────────────────────────

def insight(username: str):
    """Deep-dive analysis of an X/Twitter account."""
    username = username.lstrip("@")
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW INSIGHT — @{username}")
    print(f"{'=' * 60}")

    # 1. Profile (structured API — stable)
    print("\n  Fetching profile...")
    info = _api(client, "/v1/x/users/info", {"username": username})
    d = info.get("data", {})
    # Handle nested data (API returns {"data": {"data": {...}}})
    if isinstance(d.get("data"), dict):
        d = d["data"]

    followers = d.get("followers") or d.get("followersCount") or 0
    following = d.get("following") or d.get("followingCount") or 0
    tweets = d.get("statusesCount") or d.get("tweetsCount") or 0
    verified = d.get("isBlueVerified", False)
    bio = d.get("description") or d.get("bio") or ""
    name = d.get("name") or username

    print(f"\n  PROFILE")
    print(f"  {'Name:':<14} {name}")
    print(f"  {'Bio:':<14} {bio[:120]}")
    print(f"  {'Followers:':<14} {followers:,}")
    print(f"  {'Following:':<14} {following:,}")
    print(f"  {'Tweets:':<14} {tweets:,}")
    print(f"  {'Verified:':<14} {'Yes' if verified else 'No'}")
    if followers and following:
        ratio = followers / max(following, 1)
        print(f"  {'F/F Ratio:':<14} {ratio:.1f}x")

    # 2. Mentions (structured API — stable)
    print("\n  Fetching mentions...")
    mentions = _api(client, "/v1/x/users/mentions", {"username": username})
    mention_tweets = mentions.get("tweets", [])

    print(f"\n  MENTIONS ({len(mention_tweets)} recent)")
    for tw in mention_tweets[:5]:
        _print_tweet(tw)

    # 3. Followers (structured API — stable)
    print("\n  Fetching followers...")
    fdata = _api(client, "/v1/x/users/followers", {"username": username})
    follower_list = fdata.get("followers", [])

    top_followers = sorted(
        follower_list, key=lambda x: x.get("followers_count", 0), reverse=True
    )[:10]

    print(f"\n  TOP FOLLOWERS (by their follower count)")
    for f in top_followers:
        v = "+" if f.get("isBlueVerified") else " "
        fname = f.get("userName", "?")
        fc = f.get("followers_count", 0)
        print(f"    {v} @{fname:<22} {fc:>10,} followers")

    # 4. Recent tweets (smart — API with Grok fallback)
    print("\n  Fetching recent tweets...")
    tweets_result = _smart_user_tweets(client, username)
    _print_grok_result(tweets_result, "RECENT TWEETS")

    # 5. Engagement analysis from mentions
    if mention_tweets:
        total_likes = sum(tw.get("likeCount", 0) for tw in mention_tweets)
        total_rts = sum(tw.get("retweetCount", 0) for tw in mention_tweets)
        avg_likes = total_likes / len(mention_tweets)
        avg_rts = total_rts / len(mention_tweets)
        print(f"\n  MENTION ENGAGEMENT (last {len(mention_tweets)} mentions)")
        print(f"    Avg likes per mention:    {avg_likes:.1f}")
        print(f"    Avg retweets per mention: {avg_rts:.1f}")
        print(f"    Total reach (likes+RTs):  {total_likes + total_rts:,}")

    _print_cost(client)
    client.close()


# ── Workflow 2: Topic Radar ─────────────────────────────────────

def radar(topic: str):
    """What's hot on X/Twitter around a topic."""
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW RADAR — \"{topic}\"")
    print(f"{'=' * 60}")

    # 1. Trending (structured API — stable)
    print("\n  Fetching trending topics...")
    trending = _api(client, "/v1/x/trending", {})
    topics = trending.get("data", {}).get("topics", [])

    print(f"\n  TRENDING NOW (top 10)")
    for t in topics[:10]:
        name = t.get("name", "?")
        articles = t.get("articleCount", 0)
        views = t.get("totalViews", 0)
        match = " <--" if topic.lower() in name.lower() else ""
        print(f"    {name:<28} {articles:>4} articles  {views:>12,} views{match}")

    # 2. Search latest (smart — API with Grok fallback)
    print(f"\n  Searching \"{topic}\"...")
    search_result = _smart_search(client, topic, "Latest")
    _print_grok_result(search_result, "LATEST TWEETS")

    # 3. Top tweets (smart — API with Grok fallback)
    print(f"\n  Searching top tweets...")
    top_result = _smart_search(client, topic, "Top")
    _print_grok_result(top_result, "TOP PERFORMING TWEETS")

    # 4. Rising articles (structured API — stable)
    print("\n  Fetching rising articles...")
    rising = _api(client, "/v1/x/articles/rising", {})
    articles = rising.get("data", {}).get("articles", [])

    relevant = [a for a in articles if topic.lower() in json.dumps(a).lower()]
    show_articles = relevant[:5] if relevant else articles[:5]

    print(f"\n  RISING ARTICLES {'(topic-related)' if relevant else '(general)'}")
    for a in show_articles:
        title = a.get("title", "?")[:70]
        url = a.get("url", "")
        score = a.get("score", "?")
        print(f"    [{score}] {title}")
        if url:
            print(f"         {url[:80]}")

    # 5. Engagement summary
    if search_result["source"] == "api":
        search_tweets = search_result["data"].get("tweets", [])
        if search_tweets:
            total_likes = sum(tw.get("likeCount", 0) for tw in search_tweets)
            total_rts = sum(tw.get("retweetCount", 0) for tw in search_tweets)
            print(f"\n  TOPIC PULSE")
            print(f"    Total engagement (latest {len(search_tweets)} tweets): {total_likes + total_rts:,}")
            print(f"    Avg likes per tweet: {total_likes / len(search_tweets):.1f}")

    _print_cost(client)
    client.close()


# ── Workflow 3: Competitor Compare ──────────────────────────────

def compare(user1: str, user2: str):
    """Side-by-side comparison of two X accounts."""
    user1 = user1.lstrip("@")
    user2 = user2.lstrip("@")
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW COMPARE — @{user1} vs @{user2}")
    print(f"{'=' * 60}")

    # Profiles (structured API — stable)
    print("\n  Fetching profiles...")
    info1 = _api(client, "/v1/x/users/info", {"username": user1}).get("data", {})
    info2 = _api(client, "/v1/x/users/info", {"username": user2}).get("data", {})
    if isinstance(info1.get("data"), dict): info1 = info1["data"]
    if isinstance(info2.get("data"), dict): info2 = info2["data"]

    def _get(d, *keys):
        for k in keys:
            if d.get(k):
                return d[k]
        return 0

    f1 = _get(info1, "followersCount", "followers")
    f2 = _get(info2, "followersCount", "followers")
    fw1 = _get(info1, "followingCount", "following")
    fw2 = _get(info2, "followingCount", "following")
    t1 = _get(info1, "statusesCount", "tweetsCount")
    t2 = _get(info2, "statusesCount", "tweetsCount")

    print(f"\n  {'METRIC':<20} {'@' + user1:>18} {'@' + user2:>18}")
    print(f"  {'-' * 56}")
    print(f"  {'Followers':<20} {f1:>18,} {f2:>18,}")
    print(f"  {'Following':<20} {fw1:>18,} {fw2:>18,}")
    print(f"  {'Tweets':<20} {t1:>18,} {t2:>18,}")

    v1 = "Yes" if info1.get("isBlueVerified") else "No"
    v2 = "Yes" if info2.get("isBlueVerified") else "No"
    print(f"  {'Verified':<20} {v1:>18} {v2:>18}")

    r1 = f1 / max(fw1, 1)
    r2 = f2 / max(fw2, 1)
    print(f"  {'F/F Ratio':<20} {r1:>17.1f}x {r2:>17.1f}x")

    # Mentions (structured API — stable)
    print("\n  Fetching mentions...")
    m1 = _api(client, "/v1/x/users/mentions", {"username": user1}).get("tweets", [])
    m2 = _api(client, "/v1/x/users/mentions", {"username": user2}).get("tweets", [])

    ml1 = sum(tw.get("likeCount", 0) for tw in m1)
    ml2 = sum(tw.get("likeCount", 0) for tw in m2)
    mr1 = sum(tw.get("retweetCount", 0) for tw in m1)
    mr2 = sum(tw.get("retweetCount", 0) for tw in m2)

    print(f"\n  {'MENTIONS':<20} {'@' + user1:>18} {'@' + user2:>18}")
    print(f"  {'-' * 56}")
    print(f"  {'Recent mentions':<20} {len(m1):>18} {len(m2):>18}")
    print(f"  {'Total likes':<20} {ml1:>18,} {ml2:>18,}")
    print(f"  {'Total RTs':<20} {mr1:>18,} {mr2:>18,}")
    if m1:
        print(f"  {'Avg likes/mention':<20} {ml1/len(m1):>17.1f} ", end="")
    else:
        print(f"  {'Avg likes/mention':<20} {'--':>18} ", end="")
    if m2:
        print(f"{ml2/len(m2):>17.1f}")
    else:
        print(f"{'--':>18}")

    # Followers (structured API — stable)
    print("\n  Fetching followers...")
    fl1 = _api(client, "/v1/x/users/followers", {"username": user1}).get("followers", [])
    fl2 = _api(client, "/v1/x/users/followers", {"username": user2}).get("followers", [])

    top1 = sorted(fl1, key=lambda x: x.get("followers_count", 0), reverse=True)[:3]
    top2 = sorted(fl2, key=lambda x: x.get("followers_count", 0), reverse=True)[:3]

    print(f"\n  TOP FOLLOWERS")
    print(f"  @{user1}:")
    for f in top1:
        print(f"    @{f.get('userName', '?'):<20} {f.get('followers_count', 0):>10,}")
    print(f"  @{user2}:")
    for f in top2:
        print(f"    @{f.get('userName', '?'):<20} {f.get('followers_count', 0):>10,}")

    # Verdict
    print(f"\n  QUICK TAKE")
    if f1 > f2:
        print(f"    @{user1} has {f1/max(f2,1):.1f}x more followers")
    else:
        print(f"    @{user2} has {f2/max(f1,1):.1f}x more followers")

    if ml1 + mr1 > ml2 + mr2:
        print(f"    @{user1} gets more mention engagement ({ml1+mr1:,} vs {ml2+mr2:,})")
    else:
        print(f"    @{user2} gets more mention engagement ({ml2+mr2:,} vs {ml1+mr1:,})")

    _print_cost(client)
    client.close()


# ── Workflow 4: Engage ──────────────────────────────────────────

def engage(username: str, product: str = None):
    """
    Find unanswered mentions & high-value conversations, generate reply drafts.

    Combines structured mentions API with Grok AI analysis.
    """
    username = username.lstrip("@")
    client = _get_client()

    products_context = product or "ClawRouter (LLM router, 41+ models, 92% cost savings) and SocialClaw (X/Twitter intelligence)"

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW ENGAGE — @{username}")
    print(f"{'=' * 60}")

    # 1. Get mentions (structured API — stable)
    print("\n  Fetching mentions...")
    mentions = _api(client, "/v1/x/users/mentions", {"username": username})
    mention_tweets = mentions.get("tweets", [])

    print(f"\n  INCOMING MENTIONS ({len(mention_tweets)} found)")
    for tw in mention_tweets[:10]:
        _print_tweet(tw, max_text=150)
        print()

    # 2. Use Grok to analyze mentions and find reply-worthy ones
    print("\n  Analyzing with Grok...")

    mention_summary = []
    for tw in mention_tweets[:15]:
        author = tw.get("author", {})
        mention_summary.append({
            "handle": author.get("userName", "?"),
            "followers": author.get("followers", author.get("followersCount", 0)),
            "text": tw.get("text", "")[:200],
            "likes": tw.get("likeCount", 0),
            "rts": tw.get("retweetCount", 0),
            "link": _tweet_link(tw),
        })

    engage_messages = [
        {"role": "system", "content":
            "You are a social media growth strategist for a crypto/AI startup. "
            "Generate authentic, value-adding replies — never generic or spammy. "
            "Always include the tweet URL in your output."},
        {"role": "user", "content":
            f"""Analyze these mentions of @{username} and generate engagement replies.

MENTIONS:
{json.dumps(mention_summary, indent=2)}

PRODUCTS TO PROMOTE (when relevant):
{products_context}

For each mention that deserves a reply, output:
1. PRIORITY: high/medium/low (based on author followers, engagement, relevance)
2. TWEET: the original tweet text and link
3. REPLY DRAFT: a natural, non-spammy reply that adds value. If relevant, mention the product.
4. REASON: why this mention is worth replying to

Skip mentions that are just "GM", emoji-only, or spam.
Focus on: questions, feature requests, comparisons, high-follower accounts, and conversations about LLM costs/AI agents/crypto payments.

Output as structured text, not JSON."""},
    ]
    engage_result = client.chat_completion(
        "xai/grok-3",
        engage_messages,
        max_tokens=3000,
    )
    analysis = engage_result.choices[0].message.content or ""

    print(f"\n  ENGAGEMENT RECOMMENDATIONS")
    print(f"  {'-' * 56}")
    print(analysis)

    # 3. Also find high-value conversations to join (Grok Live Search)
    print(f"\n  Finding conversations to join...")
    opportunities = _grok_search(
        client,
        f"Find recent high-engagement tweets (50+ likes) about LLM API costs, "
        f"AI agent infrastructure, model routing, or crypto payments for AI. "
        f"These are opportunities for @{username} to reply and promote their products. "
        f"For each tweet, include: author, text, likes, URL, and a suggested reply angle.",
        min_likes=50,
        max_results=10,
    )

    print(f"\n  HIGH-VALUE CONVERSATION OPPORTUNITIES")
    print(f"  {'-' * 56}")
    print(opportunities)

    _print_cost(client)
    client.close()


# ── Workflow 5: Check ───────────────────────────────────────────

def check(username: str):
    """
    Verify posted tweets and check engagement.
    Uses Grok Live Search for reliable tweet fetching (no 502).
    """
    username = username.lstrip("@")
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW CHECK — @{username}")
    print(f"{'=' * 60}")

    # 1. Profile stats (structured API — stable)
    print("\n  Fetching profile...")
    info = _api(client, "/v1/x/users/info", {"username": username})
    d = info.get("data", {})
    if isinstance(d.get("data"), dict): d = d["data"]

    followers = d.get("followers") or d.get("followersCount") or 0
    print(f"  Followers: {followers:,}")

    # 2. Latest tweets via Grok (reliable, no 502)
    print("\n  Fetching latest tweets via Grok...")
    tweets_text = _grok_search(
        client,
        f"Show me the latest 15 tweets from @{username} (posted in the last 24 hours). "
        f"For each tweet include:\n"
        f"- Full text\n"
        f"- Like count\n"
        f"- Retweet count\n"
        f"- Reply count (if available)\n"
        f"- View/impression count (if available)\n"
        f"- Direct URL\n"
        f"- Whether it's a reply, quote tweet, or original tweet\n\n"
        f"Sort by engagement (likes + retweets) descending.",
        max_results=15,
    )

    print(f"\n  LATEST TWEETS & ENGAGEMENT")
    print(f"  {'-' * 56}")
    print(tweets_text)

    # 3. Mention activity (structured API — stable)
    print("\n  Fetching new mentions...")
    mentions = _api(client, "/v1/x/users/mentions", {"username": username})
    mention_tweets = mentions.get("tweets", [])

    unanswered = []
    for tw in mention_tweets[:10]:
        author = tw.get("author", {})
        handle = author.get("userName", "?")
        if handle.lower() != username.lower():
            unanswered.append(tw)

    if unanswered:
        print(f"\n  MENTIONS TO CHECK ({len(unanswered)} from others)")
        for tw in unanswered[:10]:
            _print_tweet(tw, max_text=150)
            print()
    else:
        print("\n  No new mentions from others.")

    _print_cost(client)
    client.close()


# ── Workflow 6: Search (structured API first, Grok enhancement) ─

def search(query: str, x_only: bool = True):
    """Search X/Twitter — structured API first, Grok for AI analysis."""
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW SEARCH — \"{query}\"")
    print(f"{'=' * 60}")

    # 1. Try structured API first (cheap, returns structured data)
    print("\n  Searching via structured API...")
    search_result = _smart_search(client, query, "Latest")

    if search_result["source"] == "api":
        tweets = search_result["data"].get("tweets", [])
        print(f"\n  RESULTS ({len(tweets)} tweets found)")
        for tw in tweets[:15]:
            _print_tweet(tw, max_text=120)
            print()

        # Show engagement summary
        if tweets:
            total_likes = sum(tw.get("likeCount", 0) for tw in tweets)
            total_rts = sum(tw.get("retweetCount", 0) for tw in tweets)
            print(f"  ENGAGEMENT SUMMARY")
            print(f"    Total tweets: {len(tweets)}")
            print(f"    Total likes: {total_likes:,}")
            print(f"    Total RTs: {total_rts:,}")
            print(f"    Avg likes/tweet: {total_likes / len(tweets):.1f}")

        # 2. Also get top tweets
        print(f"\n  Searching top tweets...")
        top_result = _smart_search(client, query, "Top")
        _print_grok_result(top_result, "TOP PERFORMING TWEETS")
    else:
        # Grok fallback already printed
        print(f"\n  RESULTS (via Grok Live Search)")
        print(f"  {'-' * 56}")
        print(search_result["data"])

    _print_cost(client)
    client.close()


# ── Workflow 7: Tweet Lookup ──────────────────────────────────

def tweet(tweet_id: str):
    """Look up a specific tweet by ID."""
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW TWEET — {tweet_id}")
    print(f"{'=' * 60}")

    # Extract tweet ID from URL if needed
    if "x.com/" in tweet_id or "twitter.com/" in tweet_id:
        tweet_id = tweet_id.rstrip("/").split("/")[-1]

    print("\n  Fetching tweet...")
    result = _api(client, "/v1/x/tweets/lookup", {"tweetIds": [tweet_id]})
    tweets = result.get("tweets", [])

    if tweets:
        tw = tweets[0]
        author = tw.get("author", {})
        handle = author.get("userName", "?")
        name = author.get("name", "?")
        text = tw.get("text", "")
        likes = tw.get("likeCount", 0)
        rts = tw.get("retweetCount", 0)
        replies = tw.get("replyCount", 0)
        views = tw.get("viewCount", 0)
        link = _tweet_link(tw)

        print(f"\n  TWEET")
        print(f"  {'Author:':<12} {name} (@{handle})")
        print(f"  {'Text:':<12} {text}")
        print(f"  {'Likes:':<12} {likes:,}")
        print(f"  {'Retweets:':<12} {rts:,}")
        print(f"  {'Replies:':<12} {replies:,}")
        if views:
            print(f"  {'Views:':<12} {views:,}")
        if link:
            print(f"  {'URL:':<12} {link}")

        # Get replies
        print("\n  Fetching replies...")
        replies_data = _api(client, "/v1/x/tweets/replies", {"tweetId": tweet_id})
        reply_tweets = replies_data.get("tweets", [])

        if reply_tweets:
            print(f"\n  REPLIES ({len(reply_tweets)} found)")
            for rtw in reply_tweets[:10]:
                _print_tweet(rtw, max_text=140)
                print()
    else:
        print("\n  Tweet not found or unavailable.")

    _print_cost(client)
    client.close()


# ── Workflow 8: Thread ────────────────────────────────────────

def thread(tweet_id: str):
    """Get a full thread starting from a tweet."""
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW THREAD — {tweet_id}")
    print(f"{'=' * 60}")

    # Extract tweet ID from URL if needed
    if "x.com/" in tweet_id or "twitter.com/" in tweet_id:
        tweet_id = tweet_id.rstrip("/").split("/")[-1]

    print("\n  Fetching thread...")
    result = _api(client, "/v1/x/tweets/thread", {"tweetId": tweet_id})
    tweets = result.get("tweets", [])

    if tweets:
        print(f"\n  THREAD ({len(tweets)} tweets)")
        for i, tw in enumerate(tweets, 1):
            author = tw.get("author", {})
            handle = author.get("userName", "?")
            text = tw.get("text", "")
            likes = tw.get("likeCount", 0)
            link = _tweet_link(tw)
            print(f"\n  [{i}] @{handle} ({likes:,} likes)")
            print(f"      {text}")
            if link:
                print(f"      {link}")
    else:
        print("\n  Thread not found or unavailable.")

    _print_cost(client)
    client.close()


# ── Workflow 9: Author Analytics ──────────────────────────────

def analytics(handle: str):
    """Deep author intelligence report."""
    handle = handle.lstrip("@")
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW ANALYTICS — @{handle}")
    print(f"{'=' * 60}")

    # 1. Author analytics (dedicated endpoint)
    print("\n  Fetching author analytics...")
    result = _api(client, "/v1/x/authors/analytics", {"handle": handle})

    if result:
        data = result.get("data", result)
        print(f"\n  AUTHOR ANALYTICS")
        for key, value in data.items():
            if isinstance(value, (int, float)):
                print(f"  {key:<30} {value:>15,}" if isinstance(value, int) else f"  {key:<30} {value:>15.2f}")
            elif isinstance(value, str):
                print(f"  {key:<30} {value}")
            elif isinstance(value, list):
                print(f"  {key:<30} ({len(value)} items)")
                for item in value[:5]:
                    print(f"    - {str(item)[:80]}")
            elif isinstance(value, dict):
                print(f"  {key}:")
                for k, v in value.items():
                    print(f"    {k:<28} {v}")

    # 2. Also get profile for context
    print("\n  Fetching profile...")
    info = _api(client, "/v1/x/users/info", {"username": handle})
    d = info.get("data", {})
    if isinstance(d.get("data"), dict): d = d["data"]

    followers = d.get("followers") or d.get("followersCount") or 0
    following = d.get("following") or d.get("followingCount") or 0
    bio = d.get("description") or d.get("bio") or ""

    print(f"\n  PROFILE CONTEXT")
    print(f"  {'Followers:':<14} {followers:,}")
    print(f"  {'Following:':<14} {following:,}")
    print(f"  {'Bio:':<14} {bio[:120]}")

    _print_cost(client)
    client.close()


# ── Workflow 10: Brief ─────────────────────────────────────────

def brief(username: str):
    """Morning brief — mentions, trends, top followers, action items."""
    username = username.lstrip("@")
    client = _get_client()

    print(f"\n{'=' * 60}")
    print(f"  SOCIALCLAW BRIEF — @{username}")
    print(f"{'=' * 60}")

    # 1. Profile
    print("\n  Fetching profile...")
    info = _api(client, "/v1/x/users/info", {"username": username})
    d = info.get("data", {})
    if isinstance(d.get("data"), dict):
        d = d["data"]

    followers = d.get("followers") or d.get("followersCount") or 0
    bio = d.get("description") or d.get("bio") or ""
    print(f"\n  PROFILE")
    print(f"  Followers: {followers:,}")
    if bio:
        print(f"  Bio: {bio[:100]}")

    # 2. Mentions
    print("\n  Fetching mentions...")
    mentions = _api(client, "/v1/x/users/mentions", {"username": username})
    mention_tweets = mentions.get("tweets", [])

    print(f"\n  OVERNIGHT MENTIONS ({len(mention_tweets)} new)")
    for tw in mention_tweets[:8]:
        _print_tweet(tw, max_text=120)
        print()

    # 3. Trending
    print("  Fetching trends...")
    trending = _api(client, "/v1/x/trending", {})
    topics = trending.get("data", {}).get("topics", [])

    print(f"\n  TRENDING NOW")
    for t in topics[:5]:
        name = t.get("name", "?")
        views = t.get("totalViews", 0)
        print(f"    {name:<24} {views:>15,} views")

    # 4. Top followers
    print("\n  Fetching followers...")
    fdata = _api(client, "/v1/x/users/followers", {"username": username})
    flist = fdata.get("followers", [])
    top = sorted(flist, key=lambda x: x.get("followers_count", 0), reverse=True)[:5]

    print(f"\n  TOP FOLLOWERS")
    for f in top:
        print(f"    @{f.get('userName', '?'):<22} {f.get('followers_count', 0):>10,} followers")

    # 5. Suggested actions
    print(f"\n  SUGGESTED ACTIONS")
    if mention_tweets:
        top_mention = max(
            mention_tweets[:15],
            key=lambda t: (t.get("author", {}).get("followers", 0)
                           or t.get("author", {}).get("followersCount", 0) or 0),
        )
        a = top_mention.get("author", {})
        h = a.get("userName", "?")
        fc = a.get("followers", a.get("followersCount", 0))
        if fc:
            print(f"    1. Reply to @{h} ({fc:,} followers) — high-value mention")
        else:
            print(f"    1. Reply to @{h} — recent mention")
    if topics:
        print(f"    2. Post about \"{topics[0]['name']}\" — {topics[0].get('totalViews', 0):,} views and trending")
    print(f"    3. Engage in top 5 threads in your niche (use hitlist)")

    _print_cost(client)
    client.close()


# ── Helpers ────────────────────────────────────────────────────

def _print_cost(client):
    s = client.get_spending()
    print(f"\n{'=' * 60}")
    print(f"  Cost: ${s['total_usd']:.4f} ({s['calls']} calls)")
    print(f"{'=' * 60}")


# ── CLI ─────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("SocialClaw v3 — X/Twitter Marketing Intelligence")
        print()
        print("  Structured APIs first, Grok AI enhancement. All via BlockRun x402.")
        print()
        print("COMMANDS:")
        print()
        print("  Account Intelligence:")
        print("    insight @username          Deep-dive: profile, mentions, followers, tweets")
        print("    analytics @username        Author intelligence report (posting patterns, reach)")
        print("    brief @username            Morning brief: mentions, trends, actions")
        print("    check @username            Verify posted tweets & check engagement")
        print()
        print("  Discovery & Search:")
        print("    search <query>             Search X (structured API + top tweets)")
        print("    radar <topic>              Trending topics + content opportunities")
        print("    tweet <id_or_url>          Look up a specific tweet + replies")
        print("    thread <id_or_url>         Get a full tweet thread")
        print()
        print("  Competitive & Engagement:")
        print("    compare @user1 @user2      Side-by-side competitor analysis")
        print("    engage @username           Find mentions & generate reply drafts")
        print()
        print("EXAMPLES:")
        print("  python3 socialclaw.py insight @elonmusk")
        print("  python3 socialclaw.py search 'AI agents crypto'")
        print("  python3 socialclaw.py radar 'Solana DeFi'")
        print("  python3 socialclaw.py tweet 1234567890123456789")
        print("  python3 socialclaw.py tweet https://x.com/user/status/1234567890123456789")
        print("  python3 socialclaw.py thread https://x.com/user/status/1234567890123456789")
        print("  python3 socialclaw.py analytics @VitalikButerin")
        print("  python3 socialclaw.py compare @solana @ethereum")
        print()
        print("COST: $0.03-$0.15 per workflow. All data saved to ~/.blockrun/data/")
        return

    cmd = sys.argv[1].lower()

    if cmd == "insight" and len(sys.argv) >= 3:
        insight(sys.argv[2])
    elif cmd == "radar" and len(sys.argv) >= 3:
        radar(" ".join(sys.argv[2:]))
    elif cmd == "compare" and len(sys.argv) >= 4:
        compare(sys.argv[2], sys.argv[3])
    elif cmd == "engage" and len(sys.argv) >= 3:
        engage(sys.argv[2], " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None)
    elif cmd == "check" and len(sys.argv) >= 3:
        check(sys.argv[2])
    elif cmd == "search" and len(sys.argv) >= 3:
        search(" ".join(sys.argv[2:]))
    elif cmd == "tweet" and len(sys.argv) >= 3:
        tweet(sys.argv[2])
    elif cmd == "thread" and len(sys.argv) >= 3:
        thread(sys.argv[2])
    elif cmd == "analytics" and len(sys.argv) >= 3:
        analytics(sys.argv[2])
    elif cmd == "brief" and len(sys.argv) >= 3:
        brief(sys.argv[2])
    else:
        print(f"Unknown: {cmd}")
        print("Commands: insight, radar, compare, engage, check, search, tweet, thread, analytics, brief")
        print("Run without arguments for full help.")


if __name__ == "__main__":
    main()
