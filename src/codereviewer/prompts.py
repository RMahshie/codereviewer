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
```mermaid
flowchart LR
    A[Component] --> B[Component]
    B --> C[Component]
```
(Only include if data flow changed. Otherwise write "No flow changes.")

Example output:

## Add thinking speed parameter to RAG queries

**What:** Allows users to select quick/normal/long processing modes that adjust model and retrieval settings.

**Why:** Gives users control over response speed vs quality tradeoff.

### Changes
- **rag_service.py**: Added `create_llm_for_speed()` to select models based on speed setting
- **query.py**: Added `thinking_speed` field to QueryRequest model
- **ThinkingSpeedSelector.tsx**: New component for speed selection UI

### Flow Impact
```mermaid
flowchart LR
    UI[ThinkingSpeedSelector] --> API[QueryRequest]
    API --> RAG[create_llm_for_speed]
    RAG --> LLM[Model Selection]
```
"""