import streamlit as st
import datetime

# --- Inline Learning Material ---
context_data = """
Getting Started with Git
-------------------------
This chapter covers the basics of Git. You will learn about version control, installing Git, and getting started with managing your source code.

About Version Control
---------------------
Version control records changes to files over time, allowing you to recall specific versions later. It is essential for collaboration and recovery.

Local and Centralized VCS
-------------------------
Local VCS methods (such as copying files) can be error prone, while centralized systems (like CVS or Subversion) manage changes on a single server, which may create a single point of failure.

Distributed Version Control Systems
-------------------------------------
Distributed systems like Git give each user a full copy of the repository, increasing reliability and flexibility.

A Short History of Git
----------------------
Git was created by Linus Torvalds in 2005 for the Linux kernel project. It is renowned for its speed, efficiency, and robust branching capabilities.
"""

# --- Utility Functions ---

def read_context(dummy_path: str) -> str:
    """
    Instead of reading from a file, return the inline learning material.
    """
    return context_data.strip()

def generate_topics(context: str) -> list:
    """
    Simulates a Gemini API call that extracts a list of topics from the context.
    For demonstration, splits the context into sentences and takes up to 5 topics.
    """
    sentences = [s.strip() for s in context.split('.') if s.strip()]
    topics = [f"Topic {i+1}: {sentence}" for i, sentence in enumerate(sentences[:5])]
    if not topics:
        topics = ["General Topic: Review the material"]
    return topics

def initialize_conversation(topic: str) -> str:
    """
    Initializes the conversation memory for a topic with a welcoming agent message.
    """
    conversation = (f"Agent: Please explain the topic '{topic}'. "
                    "To start, what do you understand by this topic?\n")
    return conversation

def get_agent_question(topic: str, conversation_memory: str, round_count: int) -> str:
    """
    Simulates a Gemini API call that generates a follow-up question based on the topic,
    conversation history, and current round of dialogue.
    """
    if round_count == 1:
        return "Agent: Why do you think this is important? Please elaborate.\n"
    elif round_count == 2:
        return "Agent: Can you provide an example or further explain your thought?\n"
    else:
        return "Agent: Thank you for your response. Moving to the next topic.\n"

def generate_summary(conversation_history: dict) -> str:
    """
    Simulates generating a summary based on the conversation history.
    """
    summary = "Summary of the conversation:\n"
    for topic, convo in conversation_history.items():
        last_line = convo.strip().splitlines()[-1]
        summary += f"- {topic}: {last_line}\n"
    return summary

# --- Main Pipeline Functions Using Chat UI ---

def run_curious_child_chat():
    """
    Main function for the "Curious Child" conversation flow using a chat interface.
    """
    # Initialize session state variables if not already set.
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "topics" not in st.session_state:
        st.session_state.topics = []
    if "current_topic_index" not in st.session_state:
        st.session_state.current_topic_index = 0
    if "round_count" not in st.session_state:
        st.session_state.round_count = 0
    if "conversation_memory" not in st.session_state:
        st.session_state.conversation_memory = ""
    if "conversation_history" not in st.session_state:
        st.session_state.conversation_history = {}

    # If topics are not generated, show a button to generate them.
    if not st.session_state.topics:
        if st.button("Generate topics to discuss"):
            context = read_context("dummy_path_not_used")
            if context:
                topics = generate_topics(context)
                st.session_state.topics = topics
                st.session_state.current_topic_index = 0
                st.session_state.conversation_history = {}
                st.session_state.round_count = 0
                current_topic = topics[0]
                st.session_state.conversation_memory = initialize_conversation(current_topic)
                # Add the initial assistant message.
                st.session_state.messages.append({"role": "assistant", "content": st.session_state.conversation_memory})
            else:
                st.error("Failed to load the study material.")
        return  # Wait for user action

    # Display current topic information.
    current_topic = st.session_state.topics[st.session_state.current_topic_index]
    st.markdown(f"### Topic {st.session_state.current_topic_index+1} of {len(st.session_state.topics)}: {current_topic}")

    # Display all previous chat messages.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input for user's response.
    user_prompt = st.chat_input("Your response:")
    if user_prompt:
        # Append user's message.
        st.session_state.messages.append({"role": "user", "content": user_prompt})
        st.session_state.conversation_memory += f"User: {user_prompt}\n"
        st.experimental_rerun()  # Refresh to display the new message

    # Process agent response if the last message is from the user.
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        st.session_state.round_count += 1
        agent_response = get_agent_question(current_topic, st.session_state.conversation_memory, st.session_state.round_count)
        st.session_state.messages.append({"role": "assistant", "content": agent_response})
        st.session_state.conversation_memory += agent_response

        # If three rounds are complete, allow moving to the next topic.
        if st.session_state.round_count >= 3:
            if st.button("Proceed to next topic"):
                st.session_state.conversation_history[current_topic] = st.session_state.conversation_memory
                st.session_state.current_topic_index += 1
                st.session_state.round_count = 0
                if st.session_state.current_topic_index < len(st.session_state.topics):
                    next_topic = st.session_state.topics[st.session_state.current_topic_index]
                    st.session_state.conversation_memory = initialize_conversation(next_topic)
                    st.session_state.messages.append({"role": "assistant", "content": st.session_state.conversation_memory})
                else:
                    st.session_state.messages.append({"role": "assistant", "content": "All topics have been discussed!"})
        st.experimental_rerun()

    # If all topics are finished, show a summary and offer a restart.
    if st.session_state.current_topic_index >= len(st.session_state.topics):
        summary = generate_summary(st.session_state.conversation_history)
        with st.chat_message("assistant"):
            st.markdown("### Summary")
            st.markdown(summary)
        if st.button("Restart"):
            for key in ["messages", "topics", "current_topic_index", "round_count", "conversation_memory", "conversation_history"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.experimental_rerun()

    # Display gamified progress.
    progress = (st.session_state.current_topic_index / len(st.session_state.topics)) if st.session_state.topics else 0
    st.progress(progress)
    st.markdown(f"**Progress:** Topic {st.session_state.current_topic_index+1} of {len(st.session_state.topics)}")

# --- Main App Setup ---

st.set_page_config(page_title="Curious Child Method", layout="wide")
st.title("💬 Curious Child Method")
st.markdown(
    """
    This application encourages you to ask "why?" and explain the studied topics.
    Respond to the agent's questions in a chat format, elaborate on your answers, and deepen your knowledge!
    """
)

run_curious_child_chat()
