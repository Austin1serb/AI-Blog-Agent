import requests
import os
from typing import Optional
import json

# # Load saved Google Search API response
# with open("google_search_sample.json", "r") as file:
#     google_response = json.load(file)

# # Set up API keys (store in environment variables for security)
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")

# Function to search Google and return the first blog post URL
def get_top_blog_post(keyword: str) -> Optional[dict]:
    # search_url = f"https://www.googleapis.com/customsearch/v1?q={keyword}&key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&num=10"
    
    # response = requests.get(search_url)
    # data = response.json()
    # print(json.dumps(data, indent=4)) 
    
    
    # ?Imitate Response during Testing:
    with open("google_search_sample.json", "r") as file:
      data = json.load(file)

    if "items" not in data:
        return None

    # Define common blog URL patterns
    blog_patterns = ["/blog/", "/post/", "/articles/", "/news/", "medium.com", "substack.com"]

    for result in data["items"]:
        url = result["link"]
        
        # Skip service pages and company homepages
        if any(x in url for x in ["/contact", "/services", "/pricing", "/about"]):
            continue

        # Check if URL looks like a blog post
        if any(pattern in url for pattern in blog_patterns):
            return {"title": result["title"], "url": url, "snippet": result["snippet"]}
    
    return None  # No blog post found

print(get_top_blog_post('web design'))