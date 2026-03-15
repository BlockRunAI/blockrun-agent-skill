# Draft Mode Prompt Template

## Context

You are helping the user write an optimized X (Twitter) post about: **{{TOPIC}}**

## Research Phase (if BlockRun available)

Search for recent high-performing posts:
```
blockrun_twitter query: "successful posts about {{TOPIC}}"
```

Look for:
- What hooks are working
- What formats get engagement
- What angles resonate

## Generation Guidelines

### Hook Selection

Choose the most appropriate hook pattern:

1. **Curiosity Gap** - Best for insights, lessons learned
   - "I've been [doing X] for [time]. Here's what I learned:"

2. **Contrarian Take** - Best for challenging assumptions
   - "Hot take: [conventional wisdom] is wrong."

3. **Specific Numbers** - Best for results, growth, metrics
   - "I went from [X] to [Y] in [time]. Here's how:"

4. **Problem Statement** - Best for solutions, tools, products
   - "[Pain point] is broken. Here's a better way:"

5. **Bold Claim** - Best for announcements, new capabilities
   - "[Capability] is now possible. [Brief explanation]"

### Structure

```
[Hook - grab attention in first line]

[Value - the insight, solution, or announcement]

[CTA - implicit question or engagement trigger]
```

### Optimization Checklist

Before finalizing, verify:
- [ ] Hook in first 280 chars (no "See more" needed for impact)
- [ ] Provides clear value (teaches, entertains, or provokes)
- [ ] Ends with engagement trigger (question, invitation to respond)
- [ ] No "I'm excited" or weak openers
- [ ] 0-2 hashtags maximum
- [ ] No ALL CAPS (except single word emphasis)
- [ ] Specific > vague (numbers, examples, details)

### Variations to Generate

1. **Different hook angle** - Same content, different opening strategy
2. **Thread opener** - If topic warrants deeper exploration
3. **Casual tone** - More conversational, less polished

## Output Format

Present the full package:
- Main post (ready to copy)
- 3 variations
- Algorithm explanation (why it should perform)
- Best practices applied
- Image suggestion if relevant
