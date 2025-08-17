import streamlit as st
import google.generativeai as genai
import uuid
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple JSON-based chat storage
class SimpleStorage:
    def __init__(self):
        self.file_path = "chat_history.json"
        self.ensure_file()
    
    def ensure_file(self):
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump({"chats": {}}, f)
    
    def save_chat(self, chat_id, messages, title):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            data["chats"][chat_id] = {
                "title": title,
                "messages": messages,
                "timestamp": datetime.now().isoformat()
            }
            
            with open(self.file_path, 'w') as f:
                json.dump(data, f)
            return True
        except:
            return False
    
    def load_chat(self, chat_id):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            return data["chats"].get(chat_id, {}).get("messages", [])
        except:
            return []
    
    def get_all_chats(self):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            chats = []
            for chat_id, chat_data in data["chats"].items():
                chats.append({
                    "id": chat_id,
                    "title": chat_data.get("title", "New Chat"),
                    "timestamp": chat_data.get("timestamp", "")
                })
            
            # Sort by timestamp (newest first)
            chats.sort(key=lambda x: x["timestamp"], reverse=True)
            return chats
        except:
            return []
    
    def delete_chat(self, chat_id):
        try:
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            if chat_id in data["chats"]:
                del data["chats"][chat_id]
                
                with open(self.file_path, 'w') as f:
                    json.dump(data, f)
                return True
            return False
        except:
            return False

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if 'chat_title' not in st.session_state:
    st.session_state.chat_title = "New Chat"
if 'storage' not in st.session_state:
    st.session_state.storage = SimpleStorage()

# Clean ChatGPT-like CSS
st.markdown("""
<style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none;}
    
    /* Main layout */
    .main {
        background-color: #212121;
        color: #ffffff;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #202123 !important;
        border-right: 1px solid #444654;
        padding-top: 1rem;
    }
    
    /* Chat container */
    .chat-container {
        max-width: 700px;
        margin: 0 auto;
        padding: 1rem;
        min-height: calc(100vh - 120px);
        padding-bottom: 120px;
    }
    
    /* Welcome screen */
    .welcome {
        text-align: center;
        padding: 2rem 1rem;
        color: #ececf1;
        margin-top: 2rem;
    }
    
    .welcome h1 {
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 1rem;
        color: #ffffff;
    }
    
    .welcome p {
        font-size: 1rem;
        opacity: 0.8;
        margin-bottom: 1rem;
    }
    
    /* Message styling */
    .user-msg {
        background: #343541;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        margin-left: 20%;
        border: 1px solid #444654;
    }
    
    .assistant-msg {
        background: #444654;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        margin-right: 20%;
        border: 1px solid #565869;
    }
    
    .msg-header {
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
        color: #ffffff;
    }
    
    .msg-content {
        color: #ececf1;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    /* Input area */
    .input-area {
        position: fixed;
        bottom: 0;
        left: 300px;
        right: 0;
        background: #343541;
        border-top: 1px solid #444654;
        padding: 1rem;
        z-index: 1000;
    }
    
    .input-wrapper {
        max-width: 700px;
        margin: 0 auto;
        position: relative;
    }
    
    /* Text area styling */
    .stTextArea > div > div > textarea {
        background: #40414f !important;
        border: 1px solid #565869 !important;
        border-radius: 8px !important;
        color: #ececf1 !important;
        font-size: 1rem !important;
        padding: 1rem !important;
        resize: none !important;
        min-height: 24px !important;
        max-height: 120px !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #10a37f !important;
        outline: none !important;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2) !important;
    }
    
    /* Send button */
    .stButton > button {
        background: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 0.5rem 1rem !important;
        font-weight: 500 !important;
        position: absolute !important;
        right: 8px !important;
        bottom: 8px !important;
        min-height: 32px !important;
        width: 32px !important;
    }
    
    .stButton > button:hover {
        background: #0d8c6f !important;
    }
    
    /* Sidebar chat items */
    .sidebar-header {
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    .stButton > button[kind="primary"] {
        background: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.75rem 1rem !important;
        width: 100% !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
        text-align: center !important;
        cursor: pointer !important;
        margin-bottom: 1rem !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: #0d8c6f !important;
    }
    
    .chat-item {
        background: transparent;
        border: none;
        color: #ececf1;
        padding: 0.75rem 1rem;
        margin: 0.2rem 0;
        border-radius: 8px;
        width: 100%;
        text-align: left;
        cursor: pointer;
        font-size: 0.85rem;
        transition: background 0.2s;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
    
    .chat-item:hover {
        background: #343541;
    }
    
    .chat-item-active {
        background: #343541;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .input-area {
            left: 0;
        }
        .chat-container {
            margin-left: 0;
        }
        .user-msg, .assistant-msg {
            margin-left: 0;
            margin-right: 0;
        }
    }
</style>
""", unsafe_allow_html=True)

# Configure Gemini API
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
except:
    st.error("Please configure your Gemini API key")
    st.stop()

def generate_response(text):
    """Generate AI response"""
    prompt = f"""
    You are a helpful AI assistant. Provide a clear, helpful response to the following:
    
    {text}
    
    Response:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}"

def new_chat():
    """Start a new chat"""
    if st.session_state.messages:
        st.session_state.storage.save_chat(
            st.session_state.chat_id,
            st.session_state.messages,
            st.session_state.chat_title
        )
    
    st.session_state.messages = []
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.chat_title = "New Chat"

def load_chat(chat_id, title):
    """Load a chat"""
    if st.session_state.messages:
        st.session_state.storage.save_chat(
            st.session_state.chat_id,
            st.session_state.messages,
            st.session_state.chat_title
        )
    
    messages = st.session_state.storage.load_chat(chat_id)
    st.session_state.messages = messages
    st.session_state.chat_id = chat_id
    st.session_state.chat_title = title

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-header">', unsafe_allow_html=True)
    
    # New Chat button with proper styling
    if st.button("+ New Chat", key="new_chat", type="primary", use_container_width=True):
        new_chat()
        st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Chat history section
    if len(st.session_state.storage.get_all_chats()) > 0:
        st.markdown("**Recent Chats**")
    
    chats = st.session_state.storage.get_all_chats()
    
    for chat in chats[:15]:  # Show last 15 chats
        chat_title = chat["title"][:25] + "..." if len(chat["title"]) > 25 else chat["title"]
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            if st.button(chat_title, key=f"chat_{chat['id']}", use_container_width=True):
                load_chat(chat["id"], chat["title"])
                st.rerun()
        
        with col2:
            if st.button("🗑", key=f"del_{chat['id']}", help="Delete"):
                st.session_state.storage.delete_chat(chat["id"])
                st.rerun()

# Main chat area
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Welcome screen or messages
if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <h1>How can I help you today?</h1>
        <p>I'm your AI assistant. Ask me anything or request help with content rewriting.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    # Display messages starting from the top
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-msg">
                <div class="msg-header">You</div>
                <div class="msg-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-msg">
                <div class="msg-header">Assistant</div>
                <div class="msg-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-area">', unsafe_allow_html=True)
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)

col1, col2 = st.columns([10, 1])

with col1:
    user_input = st.text_area(
        "",
        key="user_input",
        placeholder="Message AI Assistant...",
        label_visibility="collapsed",
        height=50
    )

with col2:
    send_btn = st.button("↑", key="send")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle input
if send_btn and user_input.strip():
    # Update title on first message
    if not st.session_state.messages:
        st.session_state.chat_title = user_input[:40] + "..." if len(user_input) > 40 else user_input
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate response
    with st.spinner("Thinking..."):
        response = generate_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Auto-save
    if len(st.session_state.messages) % 4 == 0:
        st.session_state.storage.save_chat(
            st.session_state.chat_id,
            st.session_state.messages,
            st.session_state.chat_title
        )
    
    st.session_state.user_input = ""
    st.rerun()

# Save on exit
if st.session_state.messages:
    st.session_state.storage.save_chat(
        st.session_state.chat_id,
        st.session_state.messages,
        st.session_state.chat_title
    )
