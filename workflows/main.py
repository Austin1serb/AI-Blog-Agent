from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import json
import logging


# Import functions
from core.prompt_builder import build_prompt
from tools.tokenize_text import extract_keywords_from_text
from tools.google_search import get_top_blog_post
from tools.web_scraper import extract_article_content
from typing import TypedDict, List


class WorkflowState(TypedDict):
    messages: List[HumanMessage | SystemMessage]
    blog_url: str  # Stores the blog URL
    blog_article_original: str  # Stores article text
    extracted_keywords: List  # Stores extracted keywords
    gpt_prompt: (
        List[HumanMessage | SystemMessage] | HumanMessage
    )  # GPT formatted messages


# Initialize logging
logging.basicConfig(level=logging.INFO)

# Define which model to use: "o1-preview" or "gpt-4o"
SELECTED_MODEL = "o1-preview"  # Change to "gpt-4o" when needed

# Initialize OpenAI model based on selection
if SELECTED_MODEL != "o1-preview":
    model = ChatOpenAI(model=SELECTED_MODEL, temperature=0)
else:
    model = ChatOpenAI(model=SELECTED_MODEL)


# --- Step 1: Call Google API, and get relevant Blog Article URL based on user keyword ---
def get_blog_url_from_google(state: WorkflowState) -> WorkflowState:
    """
    Parameters: Input from user
    Returns: a blog post object: blog_url:{url:www.example.com}
    """
    messages = state.get("messages", [])  # ✅ Ensure messages exist

    if not messages:
        logging.error("❌ No messages found in state!")
        return state  # Return unchanged state

    last_message = messages[-1]

    # ✅ Ensure last message is a HumanMessage before accessing `.content`
    if isinstance(last_message, HumanMessage):
        user_query = last_message.content
    elif (
        isinstance(last_message, dict) and "content" in last_message
    ):  # Handle raw dict format
        user_query = last_message["content"]
    else:
        logging.error("❌ Last message does not have a valid content field!")
        return state  # Return unchanged state

    logging.info(f"🔍 Searching Google for: {user_query}")

    blog_url = get_top_blog_post(user_query)  # ✅ Call Google API function
    logging.info(f"✅ Found Blog URL: {blog_url}")

    return {**state, "blog_url": blog_url}  # ✅ Add `blog_url` to state


# --- Step 2: Scrape blog post URL ---
def scrape_blog_url(state: WorkflowState) -> WorkflowState:
    logging.info(f"🔍 Scraping blog article...")

    # ✅ Ensure "blog_url" exists before calling .get()
    blog_url_data = state.get("blog_url", None)

    if not blog_url_data or not isinstance(blog_url_data, dict):
        logging.error("❌ No valid blog URL found in state!")
        return state  # ✅ Return unchanged state if blog_url is missing

    url = blog_url_data.get("url", None)

    if not url:
        logging.error("❌ Blog URL exists but is empty!")
        return state  # ✅ Return unchanged state

    scrapped_url = extract_article_content(url)
    logging.info(f"✅ Scraped Blog Article Successfully")

    return {**state, "blog_article_original": scrapped_url}


#  --- Step 3: Extract keyword from document ---
def extract_keywords_node(state: WorkflowState) -> WorkflowState:
    """Extracts important keywords from a reference document."""
    logging.info(f"🔍 Extracting keywords...")
    document = state.get("blog_article_original", "")
    extracted_keywords_str = extract_keywords_from_text(document)
    logging.info(f"📌 Extracted Keywords: {extracted_keywords_str}")

    # ✅ Store extracted keywords correctly as a user message
    return {**state, "extracted_keywords": extracted_keywords_str}


# --- Step 4: Prepare GPT Prompt (with Extracted Keywords) ---
def format_prompt_messages(state: WorkflowState) -> WorkflowState:
    """
    Formats messages correctly based on the selected model.

    - For `gpt-4o`: Keeps system and user messages separate.
    - For `o1-preview`: Merges everything into a single user message.

    Returns:
    - WorkflowState: Updated state with properly formatted messages.
    """
    extracted_keywords = state.get("extracted_keywords", "")
    if not extracted_keywords:
        logging.error("❌ No keywords found to build prompt..")
        return state  # ✅ Return unchanged state if no keywords found

    user_input = state.get("messages", "")
    # Generate prompt using the existing function
    prompt_messages = build_prompt(
        blog_topic=user_input, extracted_keywords_str=extracted_keywords
    )
    if SELECTED_MODEL == "o1-preview":
        # ❌ o1-preview does NOT support system messages, merge into a single user message
        combined_message = "\n\n".join([msg.content for msg in prompt_messages])

        return {
            **state,
            "gpt_prompt": [HumanMessage(content=combined_message)],
        }
    # ✅ gpt-4o supports system messages, format them properly
    return {
        **state,
        "gpt_prompt": prompt_messages,  # ✅ Store unmodified messages in state
    }


# --- Step 6: Generate Blog Article with GPT ---
def generate_blog_w_gpt(state: WorkflowState) -> WorkflowState:
    """Sends properly formatted messages to GPT and returns the response."""
    messages = state.get("gpt_prompt", [])

    if not messages:
        logging.error("❌ No formatted messages found to send to GPT.")
        return state  # Return unchanged state

    logging.info(
        f"🚀 Sending formatted messages to {SELECTED_MODEL}:\n{json.dumps([m.content for m in messages], indent=2)}"
    )

    try:
        response = model.invoke(messages)  # ✅ Call GPT model

        if not response or not response.content:
            logging.error("❌ GPT response was empty!")
            return state  # Return unchanged state if response is empty

        logging.info(f"🎉 GPT Response: {response.content}")

        # ✅ Save response as an AIMessage
        ai_message = AIMessage(content=response.content)

        return {
            **state,
            "messages": state["messages"]
            + [ai_message],  # ✅ Append to conversation history
        }

    except Exception as e:
        logging.error(f"❌ Error generating blog content: {e}")
        return state  # ✅ Return unchanged state in case of failure


# --- Step 7: Decide if Workflow Continues ---
def should_continue(state: WorkflowState) -> Literal["__end__"]:
    """Always ends the workflow for now, since iteration is not implemented yet."""
    logging.info("🚦 Workflow has completed. Ending process.")
    return "__end__"


# --- Function to Return the Workflow ---
def get_workflow():
    """Creates and compiles the LangGraph workflow."""
    workflow = StateGraph(WorkflowState)

    # ✅ Step 1: Add nodes (functions)
    workflow.add_node("get_blog_url", get_blog_url_from_google)
    workflow.add_node("scrape_blog", scrape_blog_url)
    workflow.add_node("extract_keywords", extract_keywords_node)
    workflow.add_node("format_prompt", format_prompt_messages)
    workflow.add_node("generate_blog", generate_blog_w_gpt)

    # ✅ Step 2: Define execution order (edges)
    workflow.set_entry_point("get_blog_url")  # 🔹 Start here
    workflow.add_edge("get_blog_url", "scrape_blog")
    workflow.add_edge("scrape_blog", "extract_keywords")
    workflow.add_edge("extract_keywords", "format_prompt")
    workflow.add_edge("format_prompt", "generate_blog")

    # ✅ Step 3: Conditional ending
    workflow.add_conditional_edges("generate_blog", should_continue)

    return workflow.compile()
