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
    logger.info("Starting code review")
    diff = get_diff()
    diff_stat = get_diff_stat()
    logger.info(f"Diff stats: {diff_stat}")
    summary = await summarize_changes(diff)
    if diff_stat["insertions"] > 100:
        logger.info("PR is major, running complex review")
        review = await review_commplex_changes(diff, summary)
    else:
        logger.info("PR is minor, running simple review")
        review = await review_simple_changes(diff, summary)
    
    try:
        post_comments_and_summary(review, summary)
    except Exception as e:
        logger.error(f"Error posting comments and summary: {e}")
    

if __name__ == "__main__":
    asyncio.run(main())
    