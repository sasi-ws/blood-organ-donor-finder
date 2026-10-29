import re

# One place for the scam word list (NFR-MNT-02). Add or remove words here.
SCAM_KEYWORDS = [
    "pay", "paid", "payment", "money", "price", "cash",
    "rs", "rupees", "fee", "charge",
]

# \b means "whole word only", so "pay" will not match "paycheck"-style words
# and "rs" will not match "hours".
_PATTERN = re.compile(r"\b(" + "|".join(SCAM_KEYWORDS) + r")\b", re.IGNORECASE)


def find_scam_words(text):
    """Return the money-related words found in the text (empty list if none)."""
    if not text:
        return []
    return sorted({word.lower() for word in _PATTERN.findall(text)})