# Image Mode Prompt Template

## Context

You are generating an optimized image for an X post about: **{{DESCRIPTION}}**

## BlockRun Requirement

Image generation requires BlockRun MCP with `blockrun_image` tool.

If not available, inform user:
```
Image generation requires BlockRun MCP.

Install: claude mcp add blockrun -- npx @blockrun/mcp
Fund wallet with USDC on Base (~$0.05 per image)
```

## Prompt Optimization for X

Transform user description into an optimized image prompt:

### X-Optimized Image Guidelines

1. **High Contrast** - Stops the scroll in feed
2. **Minimal Text** - Algorithm prefers native images over text-heavy graphics
3. **Bold Colors** - Stand out in timeline
4. **Simple Composition** - Clear focal point
5. **Aspect Ratio** - 1200x675 for optimal preview (16:9)

### Prompt Enhancement

Take user's description and add:
- "high contrast"
- "bold colors"
- "clean composition"
- "professional quality"
- Specific style if appropriate (minimalist, tech, abstract)

### Model Selection

Default: `google/nano-banana` (~$0.05)
- Good quality
- Fast generation
- Cost-effective

Alternative: `openai/dall-e-3` ($0.04-0.08)
- Higher fidelity
- Better text rendering
- Use for complex requests

## Generation Command

```
blockrun_image prompt: "[optimized prompt]" model: "google/nano-banana" size: "1024x1024"
```

## Output Format

Present:
1. Generated image (display or save location)
2. Image optimization tips applied
3. Suggested post to accompany the image
4. Alternative prompt if user wants variations

## Image Types by Post Category

### Announcements
- Abstract tech visuals
- Branded graphics (if user has brand colors)
- Product screenshots/mockups

### Educational Content
- Simple diagrams
- Before/after comparisons
- Visual metaphors

### Personal/Story Posts
- Abstract emotional visuals
- Relevant stock-style imagery
- Atmospheric backgrounds

### Technical Content
- Code snippets (stylized)
- Architecture diagrams
- Dashboard/UI mockups
