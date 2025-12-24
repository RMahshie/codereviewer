"""
Prompts for the code review and summarization.
"""

def get_complex_review_prompt(cwd: str, diff: str, summary: str) -> str:
    return f"""
Working directory: {cwd} (repo root)
<instructions>
Review changes from the diff. The summary describes the intent of the changes at a high level. 
Focus on finding issues not covered in the summary and high level flow breaks that are critical.

CRITICAL: You have 15 turns MAX. YOU MUST FOLLOW THE TURN LIMIT INSTRUCTIONS.
After your investigation, you MUST write your findings to /tmp/review.json
Use the Write tool to create this file with the JSON format specified below.
</instructions>

</steps>
Steps:
1. Review the diff for issues within each file.
2. For functions that are added/modified, grep for callers to check upstream impact.
3. For functions being called, grep to verify they exist and signatures match
3. Return a list of critical observations that need to be addressed.
</steps>

<summary>
{summary}
</summary>

<diff>
{diff}
</diff>

<requirements>
Do NOT:
- List files or explore structure
- Read entire files
- Include non-critical observations
- Flag .github/workflows files that call this code review action (it's the expected usage pattern)
</requirements>

<output format>
Write your findings to /tmp/review.json in this exact JSON format:
{{
  "issues": [
    {{
      "category": "Security|Logic|Performance|Maintainability",
      "file": "path/to/file.py",
      "line": 123,
      "issue": "Brief description of the issue",
      "impact": "Why this matters / what could go wrong",
      "recommendation": "How to fix it"
    }}
  ]
}}

If no critical issues found, write to /tmp/review.json:
{{
  "issues": []
}}

IMPORTANT: Use the Write tool to create /tmp/review.json with the JSON content above.
</output format>
"""

def get_simple_review_prompt(diff: str, summary: str) -> str:
    return f"""
Review this pull request diff.

## Summary
{summary}

## Diff
{diff}

Report issues that would cause bugs, crashes, security vulnerabilities, or significant maintainability problems.

For each issue, provide:
- category: Security, Logic, Complexity, etc.
- file: the filename
- line: line number
- issue: what's wrong
- impact: what could go wrong if not fixed
- recommendation: how to fix it

Examples of what to report:
- SQL injection via f-string with user input
- Division without zero check
- 150-line function with deeply nested conditions

Examples of what NOT to report:
- Minor naming improvements
- Missing type hints
- Unused imports (unless indicating missing implementation)

If no real issues exist, return an empty issues list.
"""


def get_summarizer_prompt(diff: str) -> str:
    return f"""
Summarize this pull request diff.

## Diff
{diff}

Output this exact format:

## [Verb] + [What] (e.g., "Add user authentication", "Fix cart calculation bug")

**What:** One sentence on what this PR accomplishes.

**Why:** One sentence on the motivation or problem solved.

### Changes
- **[filename]**: [what changed and why it matters]
- **[filename]**: [what changed and why it matters]

### Flow Impact
Show how NEW components connect to EXISTING ones. Mark new components.

Use:
- Solid arrows for existing connections
- Dashed arrows or "new" labels for new connections
- Subgraphs to group new vs existing
- Only show components relevant to this PR

If no architectural change (just bug fix, refactor), write "No flow changes."

Example output:

## Add webhook notification system for order events

**What:** Adds a webhook dispatcher that sends HTTP notifications when orders are created, updated, or cancelled.

**Why:** Enables third-party integrations (Slack, inventory systems) to react to order events in real-time.

### Changes
- **webhook_dispatcher.py** (new): Core dispatcher with retry logic, signature verification, and async HTTP client
- **order_service.py**: Emits events to dispatcher after order state changes
- **config.py**: Added webhook URL and secret configuration options
- **test_webhooks.py** (new): Tests for dispatcher, retry behavior, and signature generation

### Flow Impact
```mermaid
flowchart LR
    subgraph Existing
        API[Order API]
        Svc[OrderService]
        DB[(Database)]
    end
    subgraph New
        WH[WebhookDispatcher]
        Retry[RetryQueue]
    end
    API --> Svc
    Svc --> DB
    Svc -.->|"emit events"| WH
    WH -.-> Retry
    WH -.->|"POST /webhook"| External[External Services]
```

Mermaid Guidelines:
- Solid arrows (-->) = existing data flow
- Dashed arrows (-..->) = new connections added by this PR  
- Only include components touched or connected by this PR
- New modules go in "New" subgraph, modified existing in "Existing"
- Show the integration point clearly (where new meets existing)
"""