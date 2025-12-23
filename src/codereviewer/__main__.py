# main entry point for code review
# gets the diff of the pr and determines if it's a major or minor change.
# if it's major, it will run the agentic reviewer and if minor, it will run the simple reviewer.
# pr summarizer is always run.
# I use structured output to get the review and summary formated for gh comments.

from .diffs import get_diff, get_diff_stat
from .reviewer import review_commplex_changes, review_simple_changes
from .summarizer import summarize_changes
from .github_client import post_comments_and_summary
import asyncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    import os
    
    logger.info("Starting code review")
    
    # Log environment variables
    logger.info(f"GITHUB_REPOSITORY: {os.getenv('GITHUB_REPOSITORY', 'NOT SET')}")
    logger.info(f"GITHUB_PULL_REQUEST_NUMBER: {os.getenv('GITHUB_PULL_REQUEST_NUMBER', 'NOT SET')}")
    logger.info(f"API keys present - CLAUDE: {bool(os.getenv('ANTHROPIC_API_KEY'))}, OPENAI: {bool(os.getenv('OPENAI_API_KEY'))}")
    logger.info(f"GITHUB_TOKEN present: {bool(os.getenv('GITHUB_TOKEN'))}")
    
    diff = get_diff()
    diff_stat = get_diff_stat()
    logger.info(f"Diff stats: insertions={diff_stat['insertions']}, deletions={diff_stat['deletions']}, files={len(diff_stat['files'])}")
    
    summary = await summarize_changes(diff)
    logger.info(f"Summary generated: {len(summary.get('summary', ''))} chars")
    
    if diff_stat["insertions"] > 100:
        logger.info("PR is major (>100 insertions), running complex review with Claude")
        review = await review_commplex_changes(diff, summary)
    else:
        logger.info("PR is minor (<100 insertions), running simple review with OpenAI")
        review = await review_simple_changes(diff, summary)
    
    logger.info(f"Review complete: {len(review.get('issues', []))} issues found")
    
    try:
        post_comments_and_summary(review, summary)
    except Exception as e:
        logger.error(f"Error posting comments and summary: {e}", exc_info=True)
    

if __name__ == "__main__":
    asyncio.run(main())
