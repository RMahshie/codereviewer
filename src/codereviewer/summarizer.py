# planning straight up api call with the diff to chatgpt and very cheap for a general summary. give it some
# structure so it knows how to make the output look nice and readable.

from langchain_openai import ChatOpenAI
from .prompts import get_summarizer_prompt
from .models import SummaryOutput


async def summarize_changes(diff: str) -> dict:
    """
    Summarizes the changes in a pull request diff.

    Args:
        diff: The diff of the pull request.

    Returns:
        A dictionary containing the summary, has_critical_issues, and number_of_changes.
    """
    llm = ChatOpenAI(model="gpt-5-mini", temperature=0)
    structured_llm = llm.with_structured_output(SummaryOutput)
    prompt = get_summarizer_prompt(diff)
    response = structured_llm.invoke(prompt)
    return {
        "summary": response.summary, 
        "has_critical_issues": response.has_critical_issues, 
        "number_of_changes": response.number_of_changes
    }

