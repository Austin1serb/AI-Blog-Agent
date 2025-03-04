import re
from collections import Counter
from nltk.corpus import stopwords
import nltk
import yake

# Ensure stopwords are available (quietly)
nltk.download("stopwords", quiet=True)

# Precompiled regex for tokenization
WORD_PATTERN = re.compile(r'\b\w+\b')

# Cached stopwords for faster lookup
STOP_WORDS = frozenset(stopwords.words("english"))

# --------------- TEXT PROCESSING FUNCTIONS ---------------
def read_file(file_path: str) -> str:
    """Reads and returns the content of a text file."""
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

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
def extract_single_word_keywords_from_text(text: str, top_n: int = 15, min_occurrences: int = 3) -> dict:
    """
    Extracts the most frequent single-word SEO keywords from a text string.
    """
    words = tokenize_text(text)
    filtered_words = remove_stopwords(words)
    word_counts = count_frequencies(filtered_words)
    return {word: count for word, count in word_counts.most_common(top_n) if count >= min_occurrences}

def extract_single_word_keywords(file_path: str, top_n: int = 15, min_occurrences: int = 3) -> dict:
    """
    Extracts the most frequent single-word SEO keywords from a file.
    """
    text = read_file(file_path)
    return extract_single_word_keywords_from_text(text, top_n, min_occurrences)

# --------------- MULTI-WORD KEYWORD EXTRACTION USING YAKE! ---------------
def extract_long_tail_keywords(text: str, max_key_phrases: int = 20, ngram_size: int = 4) -> list:
    """
    Extracts multi-word keywords using YAKE! (filters for phrases with more than one word).
    """
    keyword_extractor = yake.KeywordExtractor(n=ngram_size, top=max_key_phrases)
    return [phrase.lower() for phrase, _ in keyword_extractor.extract_keywords(text) if " " in phrase]

def count_keyword_occurrences(text: str, keywords: list) -> dict:
    """
    Counts the frequency of each multi-word keyword in the text.
    """
    text_lower = text.lower()
    keyword_counts = {keyword: text_lower.count(keyword) for keyword in keywords}
    return {k: v for k, v in keyword_counts.items() if v > 0}

# --------------- FINAL EXTRACTION FUNCTION ---------------
def extract_all_keywords(
    file_path: str, 
    top_n: int = 30, 
    min_occurrences: int = 1, 
    max_key_phrases: int = 30, 
    ngram_size: int = 4
) -> tuple:
    """
    Extracts and returns single-word and multi-word keywords from a file.
    Reads the file only once to boost efficiency.
    """
    text = read_file(file_path)
    single_keywords = extract_single_word_keywords_from_text(text, top_n, min_occurrences)
    yake_keywords = extract_long_tail_keywords(text, max_key_phrases, ngram_size)
    multi_keyword_frequencies = count_keyword_occurrences(text, yake_keywords)
    return list(single_keywords.items()), list(multi_keyword_frequencies.items())

# --------------- FORMATTING FOR GPT ---------------
def sort_for_model(keywords: list) -> str:
    """
    Formats keyword frequency data into a ranked list for GPT input.
    Sorted by phrase length (multi-word phrases first) and frequency.
    """
    if not keywords:
        return "No relevant keywords found."
    
    sorted_keywords = sorted(keywords, key=lambda x: (x[0].count(" "), x[1]), reverse=True)
    return "Important keywords ranked by relevance:\n" + "\n".join(
        f"{i+1}. {word} ({count})" for i, (word, count) in enumerate(sorted_keywords)
    )

# --------------- SINGLE FUNCTION FOR LANGRAPH ---------------
def get_keywords_for_gpt() -> str:
    """
    Extracts keywords from 'article.txt', formats them,
    and returns a list of keywords for GPT to use in its prompt.
    """
    single_keywords, multi_keywords = extract_all_keywords(file_path='article.txt')
    # Merge multi-word keywords with single-word keywords
    keywords = multi_keywords + single_keywords
    return sort_for_model(keywords)
