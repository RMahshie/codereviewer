# main entry point for code review
# gets the diff of the pr and determines if it's a major or minor change.
# if it's major, it will run the agentic reviewer and if minor, it will run the simple reviewer.
# pr summarizer is always run.
# I use structured output to get the review and summary formated for gh comments.
