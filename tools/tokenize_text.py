import re
from collections import Counter
from nltk.corpus import stopwords
import nltk
import yake

# Ensure stopwords are available
nltk.download("stopwords", quiet=True)

# Precompiled regex for tokenization
WORD_PATTERN = re.compile(r'\b\w+\b')
STOP_WORDS = frozenset(stopwords.words("english"))

# --------------- TEXT PROCESSING FUNCTIONS ---------------
def tokenize_text(text: str) -> list:
    """Tokenizes text into lowercase words (removes punctuation)."""
    return WORD_PATTERN.findall(text.lower())

def remove_stopwords(words: list) -> list:
    """Removes stopwords from a list of words."""
    return [word for word in words if word not in STOP_WORDS]

def count_frequencies(words: list) -> Counter:
    """Counts the frequency of words in a list."""
    return Counter(words)

# --------------- SINGLE-WORD KEYWORD EXTRACTION ---------------
def extract_single_word_keywords(text: str, top_n: int = 100, min_occurrences: int = 3) -> dict:
    """Extracts frequent single-word keywords."""
    words = tokenize_text(text)
    filtered_words = remove_stopwords(words)
    word_counts = count_frequencies(filtered_words)
    return {word: count for word, count in word_counts.most_common(top_n) if count >= min_occurrences}

# --------------- MULTI-WORD KEYWORD EXTRACTION USING YAKE! ---------------
def extract_long_tail_keywords(text: str, max_key_phrases: int = 20, ngram_size: int = 4) -> list:
    """Extracts multi-word keywords using YAKE!"""
    keyword_extractor = yake.KeywordExtractor(n=ngram_size, top=max_key_phrases)
    return [phrase.lower() for phrase, _ in keyword_extractor.extract_keywords(text) if " " in phrase]

def count_keyword_occurrences(text: str, keywords: list) -> dict:
    """Counts occurrences of extracted multi-word keywords."""
    text_lower = text.lower()
    return {keyword: text_lower.count(keyword) for keyword in keywords if text_lower.count(keyword) > 0}

def sort_for_model(keywords: list) -> str:
    """
    Sorts keyword data by frequency (highest first) and returns as a formatted string.

    Parameters:
    - keywords (list): A list of tuples (word, frequency).

    Returns:
    - str: A formatted string with each keyword tuple on a new line.
    """
    if not keywords:
        return "No relevant keywords found."

    # Sort by frequency (highest first)
    sorted_keywords = sorted(keywords, key=lambda x: x[1], reverse=True)

    # Convert to a string, removing list brackets
    return ", ".join(f"('{word}', {count})" for word, count in sorted_keywords)




# --------------- MAIN FUNCTION FOR LANGRAPH ---------------
def extract_keywords_from_text(text: str) -> str:
    """Extracts keywords from raw article text instead of a file."""
    single_keywords = extract_single_word_keywords(text)
    yake_keywords = extract_long_tail_keywords(text)
    keyword_frequencies = count_keyword_occurrences(text, yake_keywords)
    
    # Merge single and multi-word keywords
    keywords = list(keyword_frequencies.items()) + list(single_keywords.items())
    return sort_for_model(keywords)

