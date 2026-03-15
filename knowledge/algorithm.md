# X Algorithm Reference

Source: [x-algorithm repo](https://github.com/xai-org/x-algorithm)

## Architecture Overview

X's "For You" feed combines:
- **In-network content** (from accounts you follow) via Thunder
- **Out-of-network content** (discovered through ML) via Phoenix

Phoenix uses a two-tower retrieval model + Grok-based transformer to predict engagement across 15 action types.

## Engagement Weights (Ranking Formula)

```
score = sum_i { weight_i * P(engagement_i) }
```

| Action | Weight | Strategy |
|--------|--------|----------|
| `reply_engaged_by_author` | **+75.0** | Reply to your own comments within 30 min |
| `reply` | **+13.5** | Spark conversation, ask questions |
| `good_profile_click` | **+12.0** | Create curiosity about you |
| `good_click` | **+11.0** | Strong hooks earn the click |
| `good_click_v2` | **+10.0** | Content worth staying for |
| `retweet` | **+1.0** | Shareable insights |
| `favorite` | **+0.5** | Lowest priority |
| `video_playback50` | **+0.005** | Watch completion matters |
| `negative_feedback_v2` | **-74.0** | "Show less" kills reach |
| `report` | **-369.0** | Devastating penalty |

**Key insight:** Author replying to comments (+75) = 150x a like (+0.5)

## Ranking Pipeline

### 1. Candidate Retrieval (~1,500 tweets)
- 50% in-network (people you follow)
- 50% out-of-network (recommendations)

### 2. Scoring (Heavy Ranker)
- Neural network with ~6,000 features
- Predicts probability of each engagement type
- Multiplies by weights above

### 3. Distribution Factors
- **SimClusters**: ~145,000 communities based on follow/engagement patterns
- **TwHIN Embeddings**: 200-dim vectors for semantic similarity
- **Tweepcred**: PageRank-based user reputation
- **RealGraph**: Relationship strength between specific users

## Critical Timing Windows

| Window | Impact |
|--------|--------|
| 0-10 minutes | Disproportionately weighted for distribution |
| First 30 min | Author engagement = +75.0 weight |
| 15+ sec dwell | Ranking boost signal |

## Penalties & Suppression

### Hard Filters (not shown)
- Blocked/muted authors
- Legal/safety violations

### Soft Downranking
- Toxicity/abuse flags
- Spam detection
- Duplicate content
- Low Tweepcred
- High negative feedback rate

### Account Health Signals
- Following/follower ratio > 0.6 = severe penalty
- Account age < 30 days = limited reach
- Bot-like patterns = suppression
- Blue Verified = 2-4x score multiplier

## Out-of-Network Distribution

To appear in non-followers' "For You":
1. Early engagement velocity (first 10 min)
2. Replies from outside your network
3. Community alignment (SimClusters)
4. Low negative feedback rate

## Feature Categories (~6,000)

- **Aggregate**: Rolling 50-day + real-time engagement
- **Interaction**: Click patterns, two-hop networks
- **Temporal**: Tweet age, account age
- **Similarity**: Embedding-based semantic matching
