# prompt_builder.py
from langchain_core.messages import SystemMessage, HumanMessage

def build_prompt(blog_topic: str, extracted_keywords_str: str, blog_length: int = 1000) -> list:
    """
    Constructs a structured prompt for an AI model to generate an SEO-optimized blog post 
    using specified keywords and image descriptions.

    Parameters:
        - blog_topic (str): The main subject of the blog.
        - extracted_keywords_str (str): A formatted string of keywords with their frequency count.
        - blog_length (int): Minimum required length of the blog post in characters. Default is 1000.

    Returns:
        - List: A structured prompt containing system and user messages.
    """

    # System prompt: Defines AI’s role, objectives, and content requirements
    system_prompt = f"""
    You are an expert content writer specializing in SEO-driven blog writing. Your task is to **reconstruct** a well-structured, 
    engaging, and human-like blog post based on a provided topic and **keyword frequency list** extracted from an existing article 
    (formatted as `<keyword_position>. <keyword> (<number_of_occurrences>)`). The goal is to **organically integrate** these keywords 
    while ensuring the content remains **high-quality, informative, and naturally engaging**.

    ### Writing Guidelines:
    - **Keyword Strategy**: Naturally integrate all provided keywords based on their frequency, ensuring they flow within the text.
      - **Prioritize high-frequency keywords**, but avoid unnatural repetition or keyword stuffing.
    - **Tone & Style**: Keep the tone **conversational, engaging, and human-like**.
      - Avoid robotic phrasing or generic AI-sounding language.
      - **Prohibited Words**: Avoid common AI marketing buzzwords like *seamless, cutting-edge, robust,* etc.
    - **Image Placement**: Include at least **three relevant image placeholders**, formatted as follows:
      - `[[Image: Concise yet descriptive caption]]`
      - Example: `[[Image: A scenic mountain view at sunrise]]`
    - **Content Structure**: Ensure the article is **reader-friendly and scannable**:
      - Use **clear headings and subheadings**.
      - Where useful, **incorporate bullet points or numbered lists** (but avoid excessive or deeply nested lists).
    - **Engagement & Depth**:
      - Support claims with **examples, statistics, expert insights, or anecdotes**.
      - Ensure the writing provides **unique value** rather than generic AI-generated fluff.
    - **SEO Best Practices**:
      - **Maintain keyword diversity** while preserving a **natural, readable flow**.
      - Use **semantic variations** and related terms instead of forcefully repeating keywords.
    - **Minimum Length Requirement**: The article must be at least **{blog_length} characters**.
    - **INCLUDE ONE HERO IMAGE AFTER THE PAGE**:

    The final article should be **reader-focused, informative, and engaging**, ensuring a **high level of expertise, depth, and SEO optimization**.
    """

    # User prompt: Provides the actual keywords and topic
    user_prompt = f"""
    **Blog Topic:** {blog_topic}
    
    **Keywords and Frequency Count:** 
    {extracted_keywords_str}
    
    Please write a **comprehensive, SEO-optimized blog post** on the above topic, ensuring meaningful and **natural** integration of the given keywords. 
    Use **image placeholders** as needed, following the specified format.

    The **quality and effectiveness** of this article are **crucial for my career**, so ensure it is **well-researched, engaging, and insightful**.
    """

    # Constructing messages for the AI
    system_message = SystemMessage(content=system_prompt)
    human_message = HumanMessage(content=user_prompt)

    return [system_message, human_message]



# print('build_prompt(web design): ', build_prompt('web design'))