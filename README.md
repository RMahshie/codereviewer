# PR Code Reviewer

AI-powered code review for GitHub PRs using Claude and OpenAI.

## Setup

1. Add secrets to your repo: `CLAUDE_API_KEY` and `OPENAI_API_KEY`
2. Create `.github/workflows/code-review.yml`:

```yaml
name: Code Review
on: [pull_request]
jobs:
  review:
    runs-on: ubuntu-latest
    permissions:
      pull-requests: write
    steps:
      - uses: RMahshie/codeReviewer@v1
        with:
          claude_api_key: ${{ secrets.CLAUDE_API_KEY }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

That's it! Reviews will now post on your PRs.
