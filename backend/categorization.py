import os
from dotenv import load_dotenv
from google import genai

load_dotenv()  #Load .env before we read any env vars

from typing import Protocol 

GEMINI_MODEL = "gemini-flash-latest"


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
    """LLM-backed categorizer. 
    
        Calls Gemini with a category-constrained prompt, validates the reply agains the allowed categories, caches successful results in memory, and falls back to the rules categorizer on an API error.
    """

    def __init__(self):
        api_key = os.environ["GEMINI_API_KEY"]    #Fail loud if LLM is ON but no key
        self._client = genai.Client(api_key=api_key)
        self._allowed = set(CATEGORY_RULES.keys())
        self._fallback = RulesCategorizer()
        self._cache: dict[str, str | None] = {}

    def categorize(self, description: str) -> str | None:
        key = description.strip().lower()
        if key in self._cache:
            return self._cache[key]
        
        categories = ", ".join(sorted(self._allowed))
        prompt = (
            "You are an expense categorizer. "
            f"Choose exactly ONE category for the expense from this list: {categories}. "
            "Reply with only the category name and nothing else. "
            "If it does not clearly fit any category, reply with the single word: None. \n"
            f"Expense description: {description}"
        )
        try:
            response = self._client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )
            answer = (response.text or "").strip().strip(".").strip()
            result = None
            for category in self._allowed:
                if answer.lower() == category.lower():
                    result = category
                    break
            self._cache[key] = result    #cache only successful LLM outcomes
            return result
        except Exception as e:
            #Any API error/timeout -> degarde gracefully to the rules engine. 
            print(f"[categorizer] LLM ERROR -> falling back to rules: {e!r}")
            return self._fallback.categorize(description)



def get_categorizer() -> Categorizer:
    """Pick the categorizer based on the CATEGORIZER env var. Defaults to rules."""
    kind = os.getenv("CATEGORIZER", "rules").strip().lower()
    if kind == "llm":
            return LLMCategorizer()
    if kind == "rules":
        return RulesCategorizer()
    #Unknown values fall back to rules for safety; the "llm" branch comes next step. 
    return RulesCategorizer()

default_categorizer: Categorizer = get_categorizer()