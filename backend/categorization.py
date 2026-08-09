from typing import Protocol 

CATEGORY_RULES = {
    "Food": ["swiggy", "zomato", "restaurant", "cafe", "coffee", "pizza"],
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

# The single instance the rest of the app imports and uses.
default_categorizer : Categorizer = RulesCategorizer()