import re
from typing import List, Optional, Tuple
from store import SearchFilters


class QueryParser:
    AVAILABLE_CATEGORIES = [
        "bread", "condiments", "dairy", "frozen", "fruits",
        "grains", "legumes", "organic", "pantry", "vegetables",
    ]
    CATEGORY_ALIASES = {
        "vegetables": ["veggies", "produce", "fresh"],
        "legumes": ["beans", "lentils", "chickpeas", "peas", "pulses"],
        "grains": ["rice", "pasta", "couscous"],
        "dairy": ["milk", "cheese", "yogurt", "butter", "eggs"],
        "fruits": ["fruit", "apple", "banana", "orange"],
    }
    DIETARY_TERMS = ["vegan", "organic", "kosher", "ready-to-eat"]
    BUY_KEYWORDS = [
        "קנה", "קנו", "קניה", "buy", "purchase", "shop",
        "add", "cart", "נקנה", "בוא נקנה", "בואו נקנה",
    ]
    _STOP_WORDS = {
        "the", "a", "an", "and", "or", "for", "with", "please",
        "shekels", "shekel", "under", "below", "less", "than",
        "list", "shopping", "products", "show", "me", "want",
        "some", "give", "get",
    }

    def parse(self, query: str) -> SearchFilters:
        q = query.lower()
        min_p, max_p = self._parse_budget(q)
        return SearchFilters(
            keywords=self._extract_keywords(q),
            categories=self._extract_categories(q),
            min_price=min_p,
            max_price=max_p,
            attributes=self._extract_attributes(q),
        )

    def needs_clarification(self, query: str) -> List[str]:
        q = query.lower()
        questions = []
        if not self._extract_categories(q):
            questions.append("📂 Which categories? (e.g., vegetables, legumes, dairy)")
        if self._parse_budget(q)[1] is None:
            questions.append("💰 Do you have a budget? (e.g., under 50 shekels, 100-200)")
        if not self._extract_attributes(q):
            questions.append("🌱 Any dietary preferences? (vegan, organic, kosher)")
        if not questions:
            questions.append("📋 What format? (markdown, JSON, CSV)")
        return questions

    def is_buy_intent(self, query: str) -> bool:
        q = query.lower()
        return any(kw in q for kw in self.BUY_KEYWORDS)

    def _parse_budget(self, q: str) -> Tuple[Optional[float], Optional[float]]:
        if any(w in q for w in ("under", "below", "less")):
            words = q.split()
            for i, word in enumerate(words):
                if word in ("under", "below", "less") and i + 1 < len(words):
                    try:
                        amount = float("".join(c for c in words[i + 1] if c.isdigit() or c == "."))
                        if amount > 0:
                            return (0.0, amount)
                    except ValueError:
                        pass
        m = re.search(r"(\d+\.?\d*)\s*-\s*(\d+\.?\d*)", q)
        if m:
            lo, hi = float(m.group(1)), float(m.group(2))
            if lo > 0 and hi > 0:
                return (lo, hi)
        return (None, None)

    def _extract_categories(self, q: str) -> List[str]:
        matched = [c for c in self.AVAILABLE_CATEGORIES if c in q or c.replace("_", " ") in q]
        for cat, aliases in self.CATEGORY_ALIASES.items():
            if cat not in matched and any(a in q for a in aliases):
                if cat in self.AVAILABLE_CATEGORIES:
                    matched.append(cat)
        return list(dict.fromkeys(matched))

    def _extract_attributes(self, q: str) -> List[str]:
        return [t for t in self.DIETARY_TERMS if t in q]

    def _extract_keywords(self, q: str) -> List[str]:
        stop = self._STOP_WORDS | set(self.BUY_KEYWORDS)
        return [w for w in q.split() if w not in stop and len(w) > 2]
