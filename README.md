# 🤖 SupportAI — Inbound Customer Support with Agentic RAG

A production-ready MVP for AI-powered multilingual inbound customer support with voice I/O, file upload, and agentic RAG — built for hackathon speed and demo clarity.

---

## ✨ Features

| Feature | Status |
|---|---|
| Dynamic time-based background (morning/afternoon/evening/night) | ✅ |
| Multilingual support (20 languages) | ✅ |
| Voice input (mic toggle) | ✅ |
| File/image attachment via `+` button | ✅ |
| Query history in sidebar | ✅ |
| New Query navigation | ✅ |
| AI response via Claude (Anthropic) | ✅ |
| Text-to-Speech voice response (gTTS) | ✅ |
| Agentic RAG (plug-in ready) | 🔧 Stub ready |

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Set your Anthropic API key

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Or create a `.env` file:
```
ANTHROPIC_API_KEY=sk-ant-...
```

### 3. Run the app

```bash
streamlit run Home.py
```

Open `http://localhost:8501` in your browser.

---

## 📁 Project Structure

```
support_agent/
├── Home.py                  ← Landing page with prompt bar
├── pages/
│   └── 1_Chat.py            ← Chat/response page
├── utils/
│   ├── session.py           ← Shared session state
│   ├── tts.py               ← Text-to-Speech (gTTS)
│   └── background.py        ← Dynamic backgrounds
├── .streamlit/
│   └── config.toml          ← Streamlit theme config
└── requirements.txt
```

---

## 🔧 Extending with RAG

In `pages/1_Chat.py`, replace the `get_ai_response()` function with your RAG pipeline:

```python
def get_ai_response(messages, language="English"):
    # Replace with your RAG agent call
    from your_rag_module import rag_agent
    query = messages[-1]["content"]
    context = rag_agent.retrieve(query)         # Vector DB retrieval
    return rag_agent.generate(query, context)    # LLM + context
```

Compatible RAG backends: LlamaIndex, LangChain, Haystack, custom FAISS/Pinecone.

---

## 🎙️ Voice Input

The mic button toggles recording state. To wire up real speech recognition:

```python
# In pages/1_Chat.py, after mic toggle:
import speech_recognition as sr

recognizer = sr.Recognizer()
with sr.Microphone() as source:
    audio = recognizer.listen(source, timeout=5)
    text = recognizer.recognize_google(audio)
    st.session_state["reply_input"] = text
```

> Note: Full browser mic access via `streamlit-webrtc` is recommended for production.

---

## 🌐 Language Support

20 languages supported out of the box: English, Hindi, Tamil, Telugu, Kannada, Malayalam, Bengali, Marathi, Gujarati, Punjabi, French, German, Spanish, Arabic, Mandarin, Japanese, Korean, Portuguese, Russian, Italian.

The LLM is instructed to respond in the selected language, and gTTS uses matching language codes for voice output.

---

## 🏆 Hackathon Tips

- **Demo flow**: Home → type query → Send → Chat page with voice response plays automatically
- **Wow factor**: Switch languages mid-conversation to show multilingual RAG
- **Upload demo**: Attach a PDF product manual, ask "what's the warranty policy?"
- **Voice demo**: Click 🎙️, speak query, show audio playback of AI response

---

Built with ❤️ using Streamlit + Anthropic Claude + gTTS
