import streamlit as st
import datetime
import time
import anthropic
import base64
from utils.session import init_session, save_query_to_history
from utils.tts import text_to_speech_base64

st.set_page_config(
    page_title="SupportAI — Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session()

# ─── Dynamic Background (same logic as home) ─────────────────────────────────
hour = datetime.datetime.now().hour
if 5 <= hour < 12:
    time_of_day = "morning"; greeting = "Good Morning ☀️"
    bg_style = "background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 30%, #ff9a9e 70%, #fecfef 100%);"
elif 12 <= hour < 17:
    time_of_day = "afternoon"; greeting = "Good Afternoon 🌤️"
    bg_style = "background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 40%, #d4fc79 80%, #96e6a1 100%);"
elif 17 <= hour < 21:
    time_of_day = "evening"; greeting = "Good Evening 🌇"
    bg_style = "background: linear-gradient(135deg, #f093fb 0%, #f5576c 30%, #fda085 60%, #f6d365 100%);"
else:
    time_of_day = "night"; greeting = "Good Night 🌙"
    bg_style = "background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);"

is_dark = time_of_day == "night"
text_color = "#ffffff" if is_dark else "#1a1a2e"
subtext_color = "rgba(255,255,255,0.75)" if is_dark else "rgba(26,26,46,0.65)"
card_bg = "rgba(255,255,255,0.15)" if is_dark else "rgba(255,255,255,0.55)"
input_bg = "rgba(255,255,255,0.25)" if is_dark else "rgba(255,255,255,0.75)"
border_col = "rgba(255,255,255,0.35)" if is_dark else "rgba(255,255,255,0.6)"
user_bubble = "linear-gradient(135deg, #7b2ff7, #f107a3)"
ai_bubble = card_bg

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

  body::before {{
    content: '';
    position: fixed; top:-50%; left:-50%;
    width:200%; height:200%;
    background: radial-gradient(ellipse at 20% 50%, rgba(120,119,198,0.12) 0%, transparent 50%),
                radial-gradient(ellipse at 80% 20%, rgba(255,200,100,0.08) 0%, transparent 40%);
    animation: drift 12s ease-in-out infinite alternate;
    pointer-events: none; z-index:0;
  }}

  @keyframes drift {{
    0% {{ transform: translate(0,0) rotate(0deg); }}
    100% {{ transform: translate(3%,2%) rotate(2deg); }}
  }}

  [data-testid="stSidebar"] {{
    background: {card_bg} !important;
    backdrop-filter: blur(20px) !important;
    border-right: 1px solid {border_col} !important;
  }}

  [data-testid="stSidebar"] * {{ color: {text_color} !important; }}

  .sidebar-title {{
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem; font-weight:700;
    letter-spacing:0.05em; margin-bottom:1rem;
    padding-bottom:0.5rem; border-bottom: 1px solid {border_col};
  }}

  .new-query-btn > button {{
    background: linear-gradient(135deg, #7b2ff7, #f107a3) !important;
    border:none !important; color:white !important;
    border-radius:14px !important; width:100% !important;
    padding:0.6rem !important; margin-bottom:1rem !important;
    font-size:0.95rem !important;
    box-shadow: 0 4px 15px rgba(123,47,247,0.35) !important;
  }}

  .stButton > button {{
    background: transparent !important;
    border: 1.5px solid {border_col} !important;
    color: {text_color} !important; border-radius:12px !important;
    font-family:'Sora',sans-serif !important; font-weight:600 !important;
    transition: all 0.2s !important; backdrop-filter: blur(10px) !important;
  }}

  .stButton > button:hover {{
    background: rgba(255,255,255,0.2) !important;
    transform: translateY(-1px) !important;
  }}

  /* Chat messages */
  .chat-container {{
    max-width: 820px; margin: 0 auto;
    padding: 1rem 1rem 6rem 1rem;
    position: relative; z-index:1;
  }}

  .chat-header {{
    text-align: center; margin-bottom: 1.5rem;
  }}

  .chat-title {{
    font-family: 'Space Mono', monospace;
    font-size: 1.5rem; font-weight:700;
    color: {text_color}; margin-bottom:0.1rem;
  }}

  .chat-subtitle {{
    font-size:0.85rem; color:{subtext_color};
  }}

  .message-row {{
    display: flex; margin-bottom: 1.25rem;
    animation: slideUp 0.3s ease-out;
  }}

  @keyframes slideUp {{
    from {{ opacity:0; transform: translateY(12px); }}
    to   {{ opacity:1; transform: translateY(0); }}
  }}

  .message-row.user {{ justify-content: flex-end; }}
  .message-row.ai   {{ justify-content: flex-start; }}

  .bubble {{
    max-width: 72%; padding: 0.9rem 1.2rem;
    border-radius: 20px; font-size:0.95rem;
    line-height: 1.55;
    box-shadow: 0 2px 12px rgba(0,0,0,0.12);
  }}

  .bubble.user {{
    background: {user_bubble};
    color: white;
    border-bottom-right-radius: 6px;
  }}

  .bubble.ai {{
    background: {ai_bubble};
    color: {text_color};
    border: 1px solid {border_col};
    backdrop-filter: blur(12px);
    border-bottom-left-radius: 6px;
  }}

  .avatar {{
    width: 34px; height: 34px; border-radius:50%;
    display:flex; align-items:center; justify-content:center;
    font-size:1rem; flex-shrink:0;
    margin: 0 0.6rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.15);
  }}

  .avatar.user {{ background: linear-gradient(135deg,#7b2ff7,#f107a3); }}
  .avatar.ai   {{ background: {input_bg}; border:1px solid {border_col}; }}

  .audio-player {{
    margin-top: 0.6rem;
    display:flex; align-items:center; gap:0.5rem;
  }}

  audio {{
    height: 32px; border-radius:8px;
    filter: {'invert(1)' if is_dark else 'none'};
    opacity: 0.85;
  }}

  .typing-indicator {{
    display:flex; gap:5px; align-items:center; padding:0.3rem;
  }}

  .typing-indicator span {{
    width:8px; height:8px; border-radius:50%;
    background: {subtext_color};
    animation: bounce 1.2s infinite;
  }}

  .typing-indicator span:nth-child(2) {{ animation-delay: 0.2s; }}
  .typing-indicator span:nth-child(3) {{ animation-delay: 0.4s; }}

  @keyframes bounce {{
    0%,60%,100% {{ transform: translateY(0); }}
    30% {{ transform: translateY(-8px); }}
  }}

  /* Bottom reply bar */
  .reply-bar {{
    position: fixed; bottom:0; left:0; right:0;
    padding: 0.75rem 1rem;
    background: {card_bg};
    backdrop-filter: blur(20px);
    border-top: 1px solid {border_col};
    z-index: 100;
  }}

  .reply-inner {{
    max-width: 820px; margin: 0 auto;
    display:flex; gap:0.5rem; align-items:flex-end;
  }}

  .reply-send > button {{
    background: linear-gradient(135deg,#7b2ff7,#f107a3) !important;
    border:none !important; color:white !important;
    border-radius:12px !important;
    box-shadow: 0 4px 15px rgba(123,47,247,0.4) !important;
  }}

  .lang-badge {{
    display:inline-block; font-size:0.72rem;
    background:{input_bg}; border:1px solid {border_col};
    border-radius:10px; padding:0.2rem 0.6rem;
    color:{subtext_color}; margin-bottom:0.5rem;
  }}

  .timestamp {{
    font-size:0.68rem; color:{subtext_color};
    margin-top:0.3rem; text-align:right;
  }}

  #MainMenu, footer, header {{ visibility:hidden; }}
  .block-container {{ padding-top:1rem !important; padding-bottom:100px !important; }}

  .stSelectbox > div > div {{
    background: transparent !important;
    border: 1px solid {border_col} !important;
    color: {text_color} !important;
  }}

  .stTextArea textarea {{
    background: transparent !important;
    border: none !important;
    color: {text_color} !important;
    font-family:'Sora',sans-serif !important;
    resize:none !important; box-shadow:none !important;
  }}

  .recording-badge {{
    display:inline-flex; align-items:center; gap:0.4rem;
    background:rgba(239,68,68,0.2); border:1px solid rgba(239,68,68,0.5);
    border-radius:20px; padding:0.3rem 0.75rem;
    font-size:0.8rem; color:#ef4444;
    animation: pulse-red 1.2s infinite;
  }}

  @keyframes pulse-red {{
    0%,100% {{ opacity:1; }} 50% {{ opacity:0.5; }}
  }}
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">🤖 SupportAI</div>', unsafe_allow_html=True)

    st.markdown('<div class="new-query-btn">', unsafe_allow_html=True)
    if st.button("＋  New Query", key="chat_new_query", use_container_width=True):
        st.session_state["chat_messages"] = []
        st.session_state["pending_query"] = ""
        st.switch_page("pages/1_Chat.py")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🏠  Home", use_container_width=True):
        st.switch_page("Home.py")

    st.markdown(f'<div style="font-size:0.78rem;color:{subtext_color};margin-bottom:0.4rem;letter-spacing:0.08em;text-transform:uppercase;">Query History</div>', unsafe_allow_html=True)

    history = st.session_state.get("query_history", [])
    if not history:
        st.markdown(f'<div style="font-size:0.82rem;color:{subtext_color};padding:0.5rem;">No queries yet.</div>', unsafe_allow_html=True)
    else:
        for i, item in enumerate(reversed(history[-15:])):
            short = item["query"][:42] + "…" if len(item["query"]) > 42 else item["query"]
            if st.button(f"💬  {short}", key=f"chat_hist_{i}", use_container_width=True):
                st.session_state["chat_messages"] = item.get("messages", [])
                st.rerun()

    st.markdown("---")
    st.markdown(f'<div style="font-size:0.72rem;color:{subtext_color};text-align:center;">Powered by Claude + RAG</div>', unsafe_allow_html=True)

# ─── Chat logic ───────────────────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

lang = st.session_state.get("selected_language", "English")
LANGUAGES = [
    "English", "Hindi", "Tamil", "Telugu", "Kannada",
    "Malayalam", "Bengali", "Marathi", "Gujarati", "Punjabi",
    "French", "German", "Spanish", "Arabic", "Mandarin",
    "Japanese", "Korean", "Portuguese", "Russian", "Italian"
]

def get_ai_response(messages, language="English"):
    """Call Anthropic API and get a response."""
    system_prompt = f"""You are SupportAI, an intelligent customer support agent with access to a knowledge base (RAG).
You help users resolve issues quickly, clearly, and empathetically.
Always respond in {language}.
Be concise but complete. Use numbered steps for procedures. 
If you don't know something, say so and offer alternatives.
Keep responses under 200 words for voice clarity."""

    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in messages
        if m["role"] in ("user", "assistant")
    ]

    try:
        import os
        api_key = st.secrets.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return "❌ API key not found. Add ANTHROPIC_API_KEY to .streamlit/secrets.toml"
        
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # ✅ correct model name
            max_tokens=512,
            system=system_prompt,
            messages=api_messages
        )
        return response.content[0].text
    except Exception as e:
        return f"Error: {str(e)}"

def render_messages():
    msgs = st.session_state.get("chat_messages", [])
    for msg in msgs:
        role = msg["role"]
        content = msg["content"]
        ts = msg.get("timestamp", "")
        audio_b64 = msg.get("audio_b64", None)

        if role == "user":
            st.markdown(f"""
            <div class="message-row user">
              <div>
                <div class="bubble user">{content}</div>
                <div class="timestamp">{ts}</div>
              </div>
              <div class="avatar user">👤</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            audio_html = ""
            if audio_b64:
                audio_html = f"""
                <div class="audio-player">
                  🔊 <audio controls autoplay>
                    <source src="data:audio/mp3;base64,{audio_b64}" type="audio/mp3">
                  </audio>
                </div>"""
            st.markdown(f"""
            <div class="message-row ai">
              <div class="avatar ai">🤖</div>
              <div>
                <div class="bubble ai">{content}{audio_html}</div>
                <div class="timestamp">{ts}</div>
              </div>
            </div>
            """, unsafe_allow_html=True)


# ─── Process pending query from home page ────────────────────────────────────
pending = st.session_state.pop("pending_query", None)
if pending:
    ts_now = datetime.datetime.now().strftime("%H:%M")
    st.session_state["chat_messages"].append({
        "role": "user",
        "content": pending,
        "timestamp": ts_now
    })
    st.session_state["needs_response"] = True

# ─── Main Chat Area ───────────────────────────────────────────────────────────
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

st.markdown(f"""
<div class="chat-header">
  <div class="chat-title">🤖 SupportAI Chat</div>
  <div class="chat-subtitle">{greeting} &nbsp;·&nbsp; <span class="lang-badge">🌐 {lang}</span></div>
</div>
""", unsafe_allow_html=True)

render_messages()

# Generate AI response if needed
if st.session_state.get("needs_response", False):
    st.session_state["needs_response"] = False

    with st.spinner(""):
        st.markdown("""
        <div class="message-row ai">
          <div class="avatar ai">🤖</div>
          <div class="bubble ai">
            <div class="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        ai_text = get_ai_response(st.session_state["chat_messages"], lang)
        audio_b64 = text_to_speech_base64(ai_text, lang)

        ts_now = datetime.datetime.now().strftime("%H:%M")
        st.session_state["chat_messages"].append({
            "role": "assistant",
            "content": ai_text,
            "timestamp": ts_now,
            "audio_b64": audio_b64
        })

        # Save to history
        user_msgs = [m for m in st.session_state["chat_messages"] if m["role"] == "user"]
        if user_msgs:
            save_query_to_history(
                query=user_msgs[-1]["content"],
                response=ai_text,
                messages=st.session_state["chat_messages"]
            )

    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ─── Fixed Reply Bar ──────────────────────────────────────────────────────────
st.markdown('<div class="reply-bar"><div class="reply-inner">', unsafe_allow_html=True)

r_plus, r_mic, r_lang, r_input, r_send = st.columns([0.5, 0.5, 1.5, 5, 1])

with r_plus:
    if st.button("＋", key="reply_plus", help="Attach files"):
        st.session_state["show_reply_upload"] = not st.session_state.get("show_reply_upload", False)

with r_mic:
    mic_lbl = "⏹" if st.session_state.get("chat_recording", False) else "🎙️"
    if st.button(mic_lbl, key="reply_mic"):
        st.session_state["chat_recording"] = not st.session_state.get("chat_recording", False)

with r_lang:
    reply_lang = st.selectbox(
        "Lang",
        LANGUAGES,
        index=LANGUAGES.index(lang) if lang in LANGUAGES else 0,
        label_visibility="collapsed",
        key="reply_lang"
    )
    st.session_state["selected_language"] = reply_lang

with r_input:
    reply_text = st.text_area(
        "Reply",
        placeholder="Type your follow-up…",
        label_visibility="collapsed",
        height=50,
        key="reply_input"
    )

with r_send:
    st.markdown('<div class="reply-send">', unsafe_allow_html=True)
    reply_send = st.button("➤", key="reply_send_btn")
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

if st.session_state.get("chat_recording", False):
    st.markdown('<div style="text-align:center;margin-top:0.5rem;"><span class="recording-badge">🔴 Recording…</span></div>', unsafe_allow_html=True)

# Show file uploader in chat
if st.session_state.get("show_reply_upload", False):
    uploaded_reply = st.file_uploader(
        "Attach files",
        type=["pdf", "png", "jpg", "jpeg", "txt", "csv", "docx"],
        accept_multiple_files=True,
        key="reply_files"
    )
    if uploaded_reply:
        st.success(f"✅ {len(uploaded_reply)} file(s) attached")

# Handle reply send
if reply_send and reply_text.strip():
    ts_now = datetime.datetime.now().strftime("%H:%M")
    st.session_state["chat_messages"].append({
        "role": "user",
        "content": reply_text.strip(),
        "timestamp": ts_now
    })
    st.session_state["needs_response"] = True
    st.rerun()
