import requests
from bs4 import BeautifulSoup
from newspaper import Article
from typing import Optional


def extract_article_content(url: str) -> Optional[str]:
    """
    Fetches and extracts the main article text from a blog post URL.
    Tries using Newspaper3k first, then falls back to BeautifulSoup.
    """
    # First, try using Newspaper3k (best for news & blogs)
    try:
        article = Article(url)
        article.download()
        article.parse()
        return article.text.strip()
    except Exception as e:
        print(f"Newspaper3k failed: {e}")

    # If Newspaper3k fails, fall back to BeautifulSoup
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            print(f"Failed to fetch page, status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")

        # Extract article content based on common article tag patterns
        article_tags = ["article", "main", "section"]
        article_content = None

        for tag in article_tags:
            article_content = soup.find(tag)
            if article_content:
                break

        if not article_content:
            print("Could not find main article content.")
            return None

        # Remove unnecessary elements like ads, scripts, sidebars
        for unwanted in article_content.find_all(
            ["script", "style", "aside", "nav", "footer"]
        ):
            unwanted.extract()

        return article_content.get_text(separator="\n", strip=True)

    except Exception as e:
        print(f"BeautifulSoup failed: {e}")
        return None


# ? Example usage
# url = get_top_blog_post("web design")['url']
# article_text = extract_article_content(url)
