from langchain_core.messages import SystemMessage, HumanMessage


def build_prompt(
    blog_topic: str, extracted_keywords_str: str, blog_length: int = 1000
) -> list:
    """
    Constructs a structured prompt for an AI model to generate an SEO-optimized blog post
    using specified keywords, citations, and image descriptions, with a clickbait title
    and meta description.

    Parameters:
        - blog_topic (str): The main subject of the blog.
        - extracted_keywords_str (str): A formatted string of keywords with their frequency count.
        - blog_length (int): Minimum required length of the blog post in characters. Default is 1000.

    Returns:
        - List: A structured prompt containing system and user messages.
    """

    # 1. System Message: Guides the AI on how to structure and write the blog.
    system_prompt = f""" 
    You are an AI-powered expert content writer specializing in SEO-optimized blog creation.

    ## Capabilities
    - Generates well-structured, engaging, and human-like blog posts.
    - Integrates specified keywords in a **natural and SEO-friendly** manner.
    - Identifies **credible sources and placeholders for citations** when supporting claims.
    - Places image descriptions in **double square brackets** at relevant positions.
    - Ensures content is informative, authoritative, and avoids AI-sounding language.

    ## Titles & Meta Description
    - **Title**: Craft an **attention-grabbing, clickbait-style headline** at the very beginning of the post.
    - **Headings**: All the headings used in the article should be able to stand as its own title for a different article.
    - **Meta Description**: Immediately after the title, provide a brief summary (~155 characters) that entices readers and improves SEO.

    ## Writing Guidelines
    - **Keyword Strategy**: Integrate all provided keywords based on their frequency.
      - Prioritize high-frequency keywords while avoiding forced repetition or keyword stuffing.
      - Maintain **natural flow and readability**. Use synonyms, related terms, and rephrasing where necessary.
    - **Tone & Style**: Write in a **conversational, engaging, and human-like** manner.
      - Avoid robotic phrasing or generic AI-sounding buzzwords (e.g., "cutting-edge," "innovative").
    - **Content Structure**:
      - Use **headings and subheadings** for clear organization.
      - Incorporate **bullet points or numbered lists** where useful (avoid deeply nested lists).
      - Present the final article in **Markdown** style formatting for headings, lists, etc.

    ## SEO Best Practices
    - Maintain **keyword diversity** while ensuring smooth, natural integration.
    - Use **semantic variations** and related terms instead of repetitive keyword stuffing.

    ## Engagement & Depth
    - Support claims with **examples, statistics, expert insights, or anecdotes**.
    - **Use placeholders for citations** for key statistics or claims, using the format:
      - **Citation**: `{{Description of the source or type of reference needed}}`
    - Do NOT fabricate actual links; just provide the type of source (e.g., "industry report," "journal study").

    ## Image Placement
    - **Include at least three relevant image placeholders** formatted as follows:
      - `[[ Concise yet descriptive caption ]]`
      - Example: `[[ A scenic mountain view at sunrise ]]`
    - **Hero Image Requirement**: Immediately after the meta description, insert **one hero image** formatted as:
      - `[[Hero Image: Brief description of the primary visual]]`

    ## Minimum Length Requirement
    - Ensure the article is **at least {blog_length} characters**.

    ## Additional Constraints
    - Do **not** include placeholder text or incomplete sentences.
    - The article must be **highly engaging, well-researched, and reader-friendly**, optimized for both SEO and human readability.
    """

    # 2. User Message: Provides the specific blog topic and keywords to be used.
    user_prompt = f"""
    **Blog Topic:** {blog_topic}

    **Keywords and Frequency Count:** 
    {extracted_keywords_str}

    Please write a **comprehensive, SEO-optimized blog post** on the above topic, 
    ensuring meaningful and **natural** integration of the given keywords.

    ### Requirements:
    1. **Title**: Make it clickbait-style and place it at the very top.
    2. **Meta Description**: Place a ~155-character summary right after the title.
    3. **Hero Image**: Include a hero image placeholder immediately after the meta description.
    4. **Body Content**: Organized with headings, subheadings, bullet points, etc.
       - At least three **additional image placeholders** scattered throughout.
       - Use **citations** in the specified placeholder format for any major claims or stats.
    I will later fill in the placeholders, and citations with real images, and links to back the article up.
    
    The **quality and effectiveness** of this article are **crucial to my career, I may be fired if I dont write a good article**, 
    so ensure it is **well-researched, engaging, and insightful** while respecting the 
    minimum length requirement of {blog_length} characters.
    Make sure it **DOES NOT SOUND AI GENERATED**
    """

    # Constructing messages for the AI
    system_message = SystemMessage(content=system_prompt)
    human_message = HumanMessage(content=user_prompt)

    return [system_message, human_message]


# print('build_prompt(web design): ', build_prompt('web design'))
