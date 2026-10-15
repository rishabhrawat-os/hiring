# Roadmap

## jd-builder

| Step | Scope | Status |
|---|---|---|
| 1. Form | Layout, fonts, blueprint, company content, renderer, design checks | Done |
| 2. Content pipeline | Initializer, researcher, VP challenger (pass ≥ 95), structurer, format challenger, copy pass with humanizer, designer | Done; first live run in this release |
| 3. Pilot | HR runs real roles across functions; tune limits and rubric from what they change by hand | Next |

Settled:
- Content comes only from the user's input and fresh research in each run. The blueprint PDFs gave layout and company details only.
- No salary, benefits or perks: the blueprint has no block for them.
- India-based roles; Bengaluru when no city is given.
- No em dashes, contrast framing or other AI writing patterns.

## resume-screener

Takes any content file from jd-builder, scores CVs against it, ranks them, and gives a go/no-go for round one. Not started.
