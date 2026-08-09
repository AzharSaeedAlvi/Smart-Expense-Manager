import os
from dotenv import load_dotenv

load_dotenv()  #Load .env before we read any env vars

from typing import Protocol 


CATEGORY_RULES = {
    "Food": ["swiggy", "zomato", "restaurant", "cafe", "coffee", "pizza",
             "lunch", "dinner", "breakfast", "meal", "food", "grocery", "groceries", "canteen"],
    "Transport": ["uber", "ola", "cab", "fuel", "petrol", "metro"],
    "Shopping": ["amazon", "flipkart", "myntra", "mall"],
    "Utilities": ["electricity", "water", "gas", "internet", "wifi", "recharge"],
    "Entertainment": ["netflix", "spotify", "movie", "bookmyshow"],
}

class Categorizer(Protocol):
    """The contract every categorizer must satisfy"""

    def categorize(self, description: str) -> str | None:
        ...

class RulesCategorizer:
    """Keyword-rules implementation of the Categorizer contract."""

    def __init__(self, rules: dict[str, list[str]] = CATEGORY_RULES):
        self._rules = rules

    def categorize(self, description: str) -> str | None:
        text = description.lower()
        for category, keywords in self._rules.items():
            if any(keyword in text for keyword in keywords):
                return category
        return None

class LLMCategorizer:
    """LLM-backed categorizer. STUB for now: returns None until the real call is wired in."""

    def categorize(self, description: str) -> str | None:
        # TODOO (next step): real LLM call here, with a rules fallback on error.
        return None


def get_catergorizer() -> Categorizer:
    """Pick the categorizer based on the CATEGORIZER env var. Defaults to rules."""
    kind = os.getenv("CATEGORIZER", "rules").strip().lower()
    if kind == "llm":
            return LLMCategorizer()
    if kind == "rules":
        return RulesCategorizer()
    #Unknown values fall back to rules for safety; the "llm" branch comes next step. 
    return RulesCategorizer()

default_categorizer: Categorizer = get_catergorizer()