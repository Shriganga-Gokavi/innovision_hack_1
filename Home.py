import streamlit as st
import datetime
from utils.session import init_session, save_query_to_history
from utils.background import get_dynamic_background

st.set_page_config(
    page_title="SupportAI — Intelligent Customer Support",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

# ─── Dynamic Background ────────────────────────────────────────────────────────
hour = datetime.datetime.now().hour
if 5 <= hour < 12:
    time_of_day = "morning"
    greeting = "Good Morning ☀️"
    bg_style = """
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 30%, #ff9a9e 70%, #fecfef 100%);
    """
elif 12 <= hour < 17:
    time_of_day = "afternoon"
    greeting = "Good Afternoon 🌤️"
    bg_style = """
        background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 40%, #d4fc79 80%, #96e6a1 100%);
    """
elif 17 <= hour < 21:
    time_of_day = "evening"
    greeting = "Good Evening 🌇"
    bg_style = """
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 30%, #fda085 60%, #f6d365 100%);
    """
else:
    time_of_day = "night"
    greeting = "Good Night 🌙"
    bg_style = """
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    """

is_dark = time_of_day == "night"
text_color = "#ffffff" if is_dark else "#1a1a2e"
subtext_color = "rgba(255,255,255,0.75)" if is_dark else "rgba(26,26,46,0.65)"
card_bg = "rgba(255,255,255,0.15)" if is_dark else "rgba(255,255,255,0.55)"
input_bg = "rgba(255,255,255,0.25)" if is_dark else "rgba(255,255,255,0.75)"
border_col = "rgba(255,255,255,0.35)" if is_dark else "rgba(255,255,255,0.6)"

# ─── Global CSS ───────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

  html, body, [data-testid="stAppViewContainer"] {{
    {bg_style}
    min-height: 100vh;
    font-family: 'Sora', sans-serif;
    color: {text_color};
  }}

  [data-testid="stAppViewContainer"] > .main {{
    background: transparent !important;
  }}

  /* Animated background particles */
  body::before {{
    content: '';
    position: fixed;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 20% 50%, rgba(120,119,198,0.15) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(255,200,100,0.1) 0%, transparent 40%);
    animation: drift 12s ease-in-out infinite alternate;
    pointer-events: none;
    z-index: 0;
  }}

  @keyframes drift {{
    0%   {{ transform: translate(0,0) rotate(0deg); }}
    100% {{ transform: translate(3%,2%) rotate(2deg); }}
  }}

  /* Sidebar styling */
  [data-testid="stSidebar"] {{
    background: {card_bg} !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid {border_col} !important;
  }}

  [data-testid="stSidebar"] * {{
    color: {text_color} !important;
  }}

  .sidebar-title {{
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid {border_col};
    color: {text_color};
  }}

  .history-item {{
    background: {input_bg};
    border: 1px solid {border_col};
    border-radius: 10px;
    padding: 0.5rem 0.75rem;
    margin: 0.4rem 0;
    font-size: 0.82rem;
    cursor: pointer;
    transition: all 0.2s;
    color: {text_color};
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }}

  .history-item:hover {{
    background: rgba(255,255,255,0.4);
    transform: translateX(3px);
  }}

  /* Main content */
  .main-container {{
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 80vh;
    padding: 2rem;
    position: relative;
    z-index: 1;
  }}

  .app-title {{
    font-family: 'Space Mono', monospace;
    font-size: clamp(2rem, 5vw, 3.5rem);
    font-weight: 700;
    text-align: center;
    letter-spacing: -0.02em;
    color: {text_color};
    margin-bottom: 0.25rem;
    text-shadow: 0 2px 20px rgba(0,0,0,0.15);
  }}

  .app-title span {{
    background: linear-gradient(90deg, #7b2ff7, #f107a3);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }}

  .greeting {{
    font-size: 1.15rem;
    font-weight: 300;
    color: {subtext_color};
    text-align: center;
    margin-bottom: 2.5rem;
    letter-spacing: 0.03em;
  }}

  /* Prompt bar wrapper */
  .prompt-wrapper {{
    width: 100%;
    max-width: 780px;
    background: {card_bg};
    backdrop-filter: blur(20px);
    border: 1.5px solid {border_col};
    border-radius: 24px;
    padding: 1rem 1.25rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15), 0 2px 8px rgba(0,0,0,0.08);
    transition: box-shadow 0.3s;
  }}

  .prompt-wrapper:focus-within {{
    box-shadow: 0 12px 48px rgba(123,47,247,0.25), 0 2px 8px rgba(0,0,0,0.1);
    border-color: rgba(123,47,247,0.5);
  }}

  /* Override Streamlit's textarea */
  .stTextArea textarea {{
    background: transparent !important;
    border: none !important;
    color: {text_color} !important;
    font-family: 'Sora', sans-serif !important;
    font-size: 1rem !important;
    resize: none !important;
    box-shadow: none !important;
    outline: none !important;
    padding: 0 !important;
  }}

  .stTextArea textarea::placeholder {{
    color: {subtext_color} !important;
  }}

  /* Buttons */
  .stButton > button {{
    background: transparent !important;
    border: 1.5px solid {border_col} !important;
    color: {text_color} !important;
    border-radius: 12px !important;
    font-family: 'Sora', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
    backdrop-filter: blur(10px) !important;
  }}

  .stButton > button:hover {{
    background: rgba(255,255,255,0.2) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 15px rgba(0,0,0,0.15) !important;
  }}

  .send-btn > button {{
    background: linear-gradient(135deg, #7b2ff7, #f107a3) !important;
    border: none !important;
    color: white !important;
    border-radius: 14px !important;
    padding: 0.5rem 1.5rem !important;
    font-size: 1rem !important;
    box-shadow: 0 4px 15px rgba(123,47,247,0.4) !important;
  }}

  .send-btn > button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(123,47,247,0.55) !important;
  }}

  .new-query-btn > button {{
    background: linear-gradient(135deg, #7b2ff7, #f107a3) !important;
    border: none !important;
    color: white !important;
    border-radius: 14px !important;
    width: 100% !important;
    padding: 0.6rem !important;
    margin-bottom: 1rem !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 15px rgba(123,47,247,0.35) !important;
  }}

  /* File upload modal-like area */
  .upload-section {{
    background: {input_bg};
    border: 1.5px dashed {border_col};
    border-radius: 16px;
    padding: 1.5rem;
    text-align: center;
    margin-top: 0.75rem;
    transition: all 0.3s;
  }}

  /* Select box */
  .stSelectbox > div > div {{
    background: transparent !important;
    border: 1px solid {border_col} !important;
    border-radius: 10px !important;
    color: {text_color} !important;
  }}

  /* Recording badge */
  .recording-badge {{
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(239,68,68,0.2);
    border: 1px solid rgba(239,68,68,0.5);
    border-radius: 20px;
    padding: 0.3rem 0.75rem;
    font-size: 0.8rem;
    color: #ef4444;
    margin-top: 0.5rem;
    animation: pulse-red 1.2s infinite;
  }}

  @keyframes pulse-red {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.5; }}
  }}

  .divider {{
    border: none;
    border-top: 1px solid {border_col};
    margin: 0.5rem 0;
  }}

  /* Hide default streamlit elements */
  #MainMenu, footer, header {{ visibility: hidden; }}
  .block-container {{ padding-top: 1rem !important; }}

  /* Tag chips */
  .feature-chip {{
    display: inline-block;
    background: {input_bg};
    border: 1px solid {border_col};
    border-radius: 20px;
    padding: 0.3rem 0.9rem;
    font-size: 0.78rem;
    color: {subtext_color};
    margin: 0.2rem;
  }}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f'<div class="sidebar-title">🤖 SupportAI</div>', unsafe_allow_html=True)

    # New Query button
    with st.container():
        st.markdown('<div class="new-query-btn">', unsafe_allow_html=True)
        if st.button("＋  New Query", key="sidebar_new_query", use_container_width=True):
            # Navigate to chat page
            st.session_state["pending_query"] = ""
            st.session_state["go_to_chat"] = True
            st.switch_page("pages/1_Chat.py")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:0.78rem; color:{subtext_color}; margin-bottom:0.4rem; letter-spacing:0.08em; text-transform:uppercase;">Query History</div>', unsafe_allow_html=True)

    history = st.session_state.get("query_history", [])
    if not history:
        st.markdown(f'<div style="font-size:0.82rem; color:{subtext_color}; padding:0.5rem;">No queries yet.</div>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(history[-15:])):
            short = item["query"][:42] + "…" if len(item["query"]) > 42 else item["query"]
            ts = item.get("timestamp", "")
            if st.button(f"💬  {short}", key=f"hist_{i}", use_container_width=True):
                st.session_state["pending_query"] = item["query"]
                st.session_state["prefill_response"] = item.get("response", "")
                st.switch_page("pages/1_Chat.py")

    st.markdown("---")
    st.markdown(f'<div style="font-size:0.72rem; color:{subtext_color}; text-align:center;">Powered by Claude + RAG</div>', unsafe_allow_html=True)

# ─── Main Content ─────────────────────────────────────────────────────────────
st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown(f'<h1 class="app-title">Support<span>AI</span></h1>', unsafe_allow_html=True)
st.markdown(f'<p class="greeting">{greeting} — How can I help you today?</p>', unsafe_allow_html=True)

# Feature chips
st.markdown(f"""
<div style="text-align:center; margin-bottom:1.5rem;">
  <span class="feature-chip">🔍 Agentic RAG</span>
  <span class="feature-chip">🌐 Multilingual</span>
  <span class="feature-chip">🎙️ Voice Input</span>
  <span class="feature-chip">📎 File Upload</span>
</div>
""", unsafe_allow_html=True)

# ─── Prompt Bar ───────────────────────────────────────────────────────────────
st.markdown('<div class="prompt-wrapper">', unsafe_allow_html=True)

# Row 1: Language selector
col_lang_label, col_lang = st.columns([1, 3])
with col_lang_label:
    st.markdown(f'<span style="font-size:0.8rem; color:{subtext_color}; line-height:2.5;">🌐 Language</span>', unsafe_allow_html=True)
with col_lang:
    LANGUAGES = [
        "English", "Hindi", "Tamil", "Telugu", "Kannada",
        "Malayalam", "Bengali", "Marathi", "Gujarati", "Punjabi",
        "French", "German", "Spanish", "Arabic", "Mandarin",
        "Japanese", "Korean", "Portuguese", "Russian", "Italian"
    ]
    selected_lang = st.selectbox(
        "Language",
        LANGUAGES,
        label_visibility="collapsed",
        key="home_lang"
    )

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Row 2: Text input area
user_query = st.text_area(
    "Ask anything…",
    placeholder="Describe your issue, ask a question, or upload a file for analysis…",
    label_visibility="collapsed",
    height=90,
    key="home_query"
)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

# Row 3: Action buttons — [+] [Mic] ... [Send]
col_plus, col_mic, col_spacer, col_send = st.columns([1, 1, 6, 1.5])

with col_plus:
    if st.button("＋", key="toggle_upload", help="Attach files or images"):
        st.session_state["show_upload"] = not st.session_state.get("show_upload", False)

with col_mic:
    mic_label = "⏹ Stop" if st.session_state.get("recording", False) else "🎙️"
    if st.button(mic_label, key="mic_btn", help="Voice input"):
        st.session_state["recording"] = not st.session_state.get("recording", False)
        if st.session_state["recording"]:
            st.session_state["mic_status"] = "recording"
        else:
            st.session_state["mic_status"] = "stopped"

with col_send:
    st.markdown('<div class="send-btn">', unsafe_allow_html=True)
    send_clicked = st.button("Send ➤", key="home_send")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close prompt-wrapper

# Recording status badge
if st.session_state.get("recording", False):
    st.markdown('<div class="recording-badge">🔴 Recording… speak your query</div>', unsafe_allow_html=True)
elif st.session_state.get("mic_status") == "stopped" and not st.session_state.get("recording", False):
    st.markdown(f'<div style="font-size:0.78rem; color:{subtext_color}; margin-top:0.3rem;">✅ Voice captured — edit above or send</div>', unsafe_allow_html=True)

# File upload panel (conditional)
if st.session_state.get("show_upload", False):
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "Drag & drop files here, or click to browse",
        type=["pdf", "png", "jpg", "jpeg", "txt", "csv", "docx", "xlsx"],
        accept_multiple_files=True,
        key="home_files"
    )
    if uploaded:
        st.success(f"✅ {len(uploaded)} file(s) attached")
        st.session_state["attached_files"] = uploaded
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close main-container

# ─── Navigate on Send ─────────────────────────────────────────────────────────
def handle_send():
    q = st.session_state.get("home_query", "").strip()
    if q:
        st.session_state["pending_query"] = q
        st.session_state["selected_language"] = st.session_state.get("home_lang", "English")
        st.session_state["attached_files"] = st.session_state.get("attached_files", [])
        st.switch_page("pages/1_Chat.py")

if send_clicked:
    handle_send()

# Keyboard Enter support via JS injection
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    const textareas = document.querySelectorAll('textarea');
    for (let ta of textareas) {
      if (document.activeElement === ta) {
        // Trigger send button
        const btns = document.querySelectorAll('button');
        for (let b of btns) {
          if (b.innerText.includes('Send')) { b.click(); break; }
        }
        e.preventDefault();
        break;
      }
    }
  }
});
</script>
""", unsafe_allow_html=True)
