import requests
import os
from typing import Optional
import json

# Load saved Google Search API response (for testing)
with open("./tests/t.json", "r") as file:
    google_response = json.load(file)

# Set up API keys (store in environment variables for security)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Define filters
BLACKLISTED_DOMAINS = ["reddit.com", "wikipedia.org", "medium.com", "quora.com", "linkedin.com", "x.com", "twitter.com"]
BLOG_PATTERNS = ["/blog/", "/post/", "/articles/",]
WHITELISTED_DOMAINS = [
    # 📝 **Marketing & Business**
    "hubspot.com", "neilpatel.com", "moz.com", "semrush.com", "ahrefs.com",
    "searchenginejournal.com", "backlinko.com", "sproutsocial.com", "contentmarketinginstitute.com",
    
    # 💻 **Technology & Software**
    "techcrunch.com", "thenextweb.com", "wired.com", "smashingmagazine.com",
    "venturebeat.com", "makeuseof.com", "readwrite.com",

    # 🔥 **Startups & Entrepreneurship**
    "forbes.com", "entrepreneur.com", "inc.com", "fastcompany.com",

    # 🛠 **Web Design & Development**
    "webflow.com/blog", "wix.com/blog", "css-tricks.com", "smashingmagazine.com",
    "speckyboy.com", "sitepoint.com", "tutsplus.com", "developer.mozilla.org",

    # 📈 **Finance & Business**
    "investopedia.com", "businessinsider.com", "thebalance.com", "nerdwallet.com",

    # 🎨 **Creativity & Design**
    "dribbble.com/stories", "creativebloq.com", "99designs.com/blog", "canva.com/blog",
    
    # 🔍 **SEO & Digital Growth**
    "searchenginewatch.com", "seroundtable.com", "cognitiveseo.com", "seoptimer.com",

    # 📊 **Data & AI**
    "towardsdatascience.com", "analyticsvidhya.com", "openai.com/research", "huggingface.co/blog",

    # ✍️ **Writing & Blogging**
    "problogger.com", "copyblogger.com", "writersdigest.com", "grammarly.com/blog",
]

def is_valid_url(url):
    """Checks if the URL is reachable and valid."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return response.status_code < 400
    except requests.RequestException:
        return False

def get_top_blog_post(keyword: str = "Web Design") -> Optional[dict]:
    """
    Searches Google for the given keyword and returns the first valid blog post.
    """
    # Uncomment this for live API requests
    # search_url = f"https://www.googleapis.com/customsearch/v1?q={keyword}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&num=10"
    # response = requests.get(search_url)
    # data = response.json()

    # Use local JSON file (for testing)
    data = google_response

    if not data.get("items"):  # Ensures "items" exists and is not empty
        return None

    for result in data["items"]:
        url = result.get("link", "").lower()  # Ensure case insensitivity
        domain = result.get("displayLink", "").lower()

        # Skip blacklisted domains
        if any(blacklisted in url for blacklisted in BLACKLISTED_DOMAINS):
            continue
        
        # Skip results without a valid link
        if len(url) < 10 or not url.startswith("http"):
            continue

        # Check if it's a blog post (by URL pattern or whitelisted domain)
        is_blog_post = any(pattern in url for pattern in BLOG_PATTERNS) or domain in WHITELISTED_DOMAINS

        # Try to use Open Graph metadata if available
        meta_tags = result.get("pagemap", {}).get("metatags", [{}])[0]
        is_article = meta_tags.get("og:type", "").lower() == "article"

        # Final validation before returning
        if (is_blog_post or is_article) and is_valid_url(url):
            return {
                "url": url,
            }

    return None  # No blog post found

# Test it
print(get_top_blog_post("web design"))