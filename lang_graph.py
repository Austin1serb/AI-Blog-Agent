from typing import Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState
from langchain_core.messages import SystemMessage, HumanMessage

import logging

# Import functions
from prompt_builder import build_prompt
from tokenize_text import get_keywords_for_gpt  # Ensure this function is imported

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Define which model to use: "o1-preview" or "gpt-4o"
SELECTED_MODEL = "o1-preview"  # Change to "gpt-4o" when needed

# Initialize OpenAI model based on selection
if SELECTED_MODEL !="o1-preview":
    model = ChatOpenAI(model=SELECTED_MODEL,temperature=0)
else:
    model=ChatOpenAI(model=SELECTED_MODEL)


# --- Step 1: Extract Keywords ---
def extract_keywords_node(state: MessagesState):
    """Extracts important keywords from a reference document."""
    logging.info(f"🔍 Extracting keywords...")

    # Call the keyword extraction function
    extracted_keywords_str = get_keywords_for_gpt()

    logging.info(f"📌 Extracted Keywords: {extracted_keywords_str}")

    # ✅ Store extracted keywords correctly as a user message
    return {"messages": [HumanMessage(content=f"Extracted Keywords: {extracted_keywords_str}")]}



# --- Step 2: Prepare GPT Prompt (with Extracted Keywords) ---
def build_prompt_node(state: MessagesState):
    """Formats prompt messages correctly based on model type."""
    user_input = state["messages"][-1].content
    extracted_keywords = state["messages"][-1].content.replace("Extracted Keywords: ", "")

    prompt_messages = build_prompt(blog_topic=user_input, extracted_keywords_str=extracted_keywords)

    logging.info(f"✅ System Prompt Generated: {prompt_messages}")

    valid_messages = []
    for msg in prompt_messages:
        if isinstance(msg, SystemMessage) and SELECTED_MODEL == "gpt-4o":
            valid_messages.append({"role": "system", "content": msg.content})
        elif isinstance(msg, HumanMessage):
            valid_messages.append({"role": "user", "content": msg.content})
        else:
            logging.warning(f"⚠️ Skipping unsupported message type for {SELECTED_MODEL}: {msg}")

    return {"messages": valid_messages}


# --- Step 3: Generate Blog Content with GPT ---

import json

def generate_blog_content(state: MessagesState):
    """Formats messages correctly depending on the model, then sends them to OpenAI."""
    messages = state["messages"]

    logging.info(f"📝 Raw messages before filtering: {messages}")

    valid_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            valid_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, SystemMessage):
            if SELECTED_MODEL == "gpt-4o":
                valid_messages.append({"role": "system", "content": msg.content})
            else:
                logging.warning(f"⚠️ Skipping SystemMessage (not supported in {SELECTED_MODEL}): {msg}")
        else:
            logging.warning(f"⚠️ Skipping unknown message type: {msg}")

    logging.info(f"🚀 Sending formatted messages to {SELECTED_MODEL}:\n{json.dumps(valid_messages, indent=2)}")

    response = model.invoke(valid_messages)

    logging.info(f"🎉 GPT Response: {response.content}")

    return {"messages": valid_messages + [{"role": "assistant", "content": response.content}]}



# --- Step 4: Decide if Workflow Continues ---
def should_continue(state: MessagesState) -> Literal["__end__", "write_article"]:
    """Checks the last AI message to decide if we continue or end the workflow."""
    messages = state["messages"]
    last_message = messages[-1]

    if "END" in last_message.content.upper():
        logging.info("🚦 Workflow is ending.")
        return "__end__"

    logging.info("🔄 Continuing workflow...")
    return "write_article"

# --- Function to Return the Workflow ---
def get_workflow():
    workflow = StateGraph(MessagesState)
    
    # Add nodes
    workflow.add_node("extract_keywords", extract_keywords_node)
    workflow.add_node("build_prompt", build_prompt_node)
    workflow.add_node("write_article", generate_blog_content)
    
    # Define workflow edges
    workflow.add_edge("__start__", "extract_keywords")  # Start with keyword extraction
    workflow.add_edge("extract_keywords", "build_prompt")  # Then generate the prompt
    workflow.add_edge("build_prompt", "write_article")  # Then send to GPT
    workflow.add_conditional_edges("write_article", should_continue)
    
    return workflow.compile()
