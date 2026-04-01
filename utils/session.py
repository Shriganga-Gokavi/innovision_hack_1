import streamlit as st
import datetime


def init_session():
    """Initialize all session state variables."""
    defaults = {
        "query_history": [],
        "chat_messages": [],
        "pending_query": "",
        "selected_language": "English",
        "show_upload": False,
        "show_reply_upload": False,
        "recording": False,
        "chat_recording": False,
        "mic_status": None,
        "needs_response": False,
        "attached_files": [],
        "go_to_chat": False,
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def save_query_to_history(query: str, response: str = "", messages: list = None):
    """Persist a query + response pair to session history."""
    if not query.strip():
        return

    if "query_history" not in st.session_state:
        st.session_state["query_history"] = []

    entry = {
        "query": query,
        "response": response,
        "messages": messages or [],
        "timestamp": datetime.datetime.now().strftime("%b %d, %H:%M"),
    }

    # Avoid duplicate consecutive entries
    history = st.session_state["query_history"]
    if history and history[-1]["query"] == query:
        history[-1] = entry
    else:
        history.append(entry)

    # Keep last 50
    st.session_state["query_history"] = history[-50:]
