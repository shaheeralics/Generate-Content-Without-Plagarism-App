import streamlit as st
import google.generativeai as genai
import uuid
from datetime import datetime
import json
import os

# Page configuration
st.set_page_config(
    page_title="ChatGPT Clone",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Developer note:
# If the sidebar still appears collapsed in deployment:
# 1. Ensure you're not embedding the app in an iframe that constrains width.
# 2. Streamlit auto-collapses when viewport width < ~750px (e.g., on small mobile) – rotate or widen.
# 3. initial_sidebar_state only applies on first load; subsequent reloads preserve user choice in browser storage.
# 4. Avoid overriding .main margin-left while also fixing sidebar; that caused hidden chat + scroll before.

# NOTE: Removed previous brittle JS that tried to force the sidebar open using a hashed CSS class.
# We'll rely on stable data-testid selectors plus Streamlit's own layout handling.

# Simple storage class
class ChatStorage:
    def __init__(self):
        self.file = "chats.json"
        self.init_file()
    
    def init_file(self):
        if not os.path.exists(self.file):
            with open(self.file, 'w') as f:
                json.dump({}, f)
    
    def save_chat(self, chat_id, messages, title):
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
            data[chat_id] = {
                "title": title,
                "messages": messages,
                "created": datetime.now().isoformat()
            }
            with open(self.file, 'w') as f:
                json.dump(data, f)
        except:
            pass
    
    def load_chat(self, chat_id):
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
            return data.get(chat_id, {}).get("messages", [])
        except:
            return []
    
    def get_chats(self):
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
            chats = []
            for cid, cdata in data.items():
                chats.append({
                    "id": cid,
                    "title": cdata.get("title", "New chat"),
                    "created": cdata.get("created", "")
                })
            chats.sort(key=lambda x: x["created"], reverse=True)
            return chats
        except:
            return []
    
    def delete_chat(self, chat_id):
        try:
            with open(self.file, 'r') as f:
                data = json.load(f)
            if chat_id in data:
                del data[chat_id]
                with open(self.file, 'w') as f:
                    json.dump(data, f)
        except:
            pass

# Initialize session
if 'storage' not in st.session_state:
    try:
        st.session_state.storage = ChatStorage()
    except Exception as e:
        st.error(f"Error initializing storage: {e}")
        st.session_state.storage = None

if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if 'title' not in st.session_state:
    st.session_state.title = "New chat"

# ChatGPT-like CSS
st.markdown("""
<style>
/* Hide Streamlit branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Main container */
.stApp {
    background-color: #212121;
}

/* Sidebar (use stable data-testid) */
[data-testid="stSidebar"] {
    background-color: #171717 !important;
    padding-top: 0 !important;
    width: 300px !important; /* Desired width */
}

/* Ensure sidebar content scrolls nicely */
[data-testid="stSidebar"] .css-1lcbmhc, /* inner container (may vary) */
[data-testid="stSidebar"] section[data-testid="stSidebarContent"] {
    padding-top: 0 !important;
}

/* Main content adjustment: remove forced extra left margin that caused horizontal scroll */
.main .block-container {
    padding-top: 0.5rem !important;
    padding-left: 1rem !important;
    padding-right: 1rem !important;
    max-width: 1100px !important;
}

/* Sidebar content */
.sidebar-content {
    padding: 0.5rem;
    height: 100vh;
    display: flex;
    flex-direction: column;
}

/* New chat button */
.new-chat-button {
    background: transparent;
    border: 1px solid #565869;
    color: #ffffff;
    padding: 0.75rem 1rem;
    border-radius: 6px;
    width: 100%;
    margin-bottom: 1rem;
    cursor: pointer;
    font-size: 14px;
    text-align: left;
    transition: background 0.2s;
}

.new-chat-button:hover {
    background: #2a2a2a;
}

/* Chat history */
.chat-history {
    flex: 1;
    overflow-y: auto;
}

.chat-item {
    background: transparent;
    border: none;
    color: #ffffff;
    padding: 0.75rem 1rem;
    margin: 0.25rem 0;
    border-radius: 6px;
    width: 100%;
    text-align: left;
    cursor: pointer;
    font-size: 14px;
    transition: background 0.2s;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.chat-item:hover {
    background: #2a2a2a;
}

/* Chat container */
.chat-container {
    display: flex;
    flex-direction: column;
    min-height: calc(100vh - 1rem);
    max-width: 768px;
    margin: 0 auto;
}

/* Messages area */
.messages-area {
    flex: 1;
    overflow-y: auto;
    padding: 1rem;
    padding-bottom: 2rem;
}

/* Welcome screen */
.welcome {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100%;
    text-align: center;
    color: #ffffff;
}

.welcome h1 {
    font-size: 2rem;
    margin-bottom: 1rem;
    font-weight: 600;
}

.welcome p {
    color: #a0a0a0;
    font-size: 1rem;
}

/* Messages */
.message {
    margin: 1.5rem 0;
    display: flex;
    align-items: flex-start;
}

.message.user {
    justify-content: flex-end;
}

.message-content {
    max-width: 70%;
    padding: 1rem 1.25rem;
    border-radius: 18px;
    word-wrap: break-word;
}

.message.user .message-content {
    background: #2f2f2f;
    color: #ffffff;
    margin-left: 2rem;
}

.message.assistant .message-content {
    background: #1a1a1a;
    color: #ffffff;
    margin-right: 2rem;
    border: 1px solid #333;
}

/* Input area */
.input-area {
    padding: 1rem;
    border-top: 1px solid #333;
    background: #212121;
}

.input-container {
    max-width: 768px;
    margin: 0 auto;
    position: relative;
    background: #2f2f2f;
    border-radius: 12px;
    border: 1px solid #565869;
}

.stTextArea > div > div > textarea {
    background: transparent !important;
    border: none !important;
    color: #ffffff !important;
    font-size: 16px !important;
    padding: 1rem !important;
    resize: none !important;
    min-height: 20px !important;
    max-height: 200px !important;
    outline: none !important;
}

.stTextArea > div > div > textarea::placeholder {
    color: #888 !important;
}

/* Send button */
.send-button {
    position: absolute;
    right: 8px;
    bottom: 8px;
    background: #10a37f;
    border: none;
    border-radius: 6px;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: white;
}

.send-button:hover {
    background: #0d8c6f;
}

.send-button:disabled {
    background: #666;
    cursor: not-allowed;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}

::-webkit-scrollbar-track {
    background: #171717;
}

::-webkit-scrollbar-thumb {
    background: #404040;
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* Responsive */
@media (max-width: 768px) {
    .message-content {
        max-width: 85%;
    }
    
    .message.user .message-content {
        margin-left: 1rem;
    }
    
    .message.assistant .message-content {
        margin-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)

# Configure AI
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
except:
    st.error("Please set up your Gemini API key")
    st.stop()

def generate_response(prompt):
    try:
        response = model.generate_content(f"You are a helpful AI assistant. Respond naturally and helpfully to: {prompt}")
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def new_chat():
    if st.session_state.messages and st.session_state.storage:
        st.session_state.storage.save_chat(
            st.session_state.chat_id,
            st.session_state.messages,
            st.session_state.title
        )
    st.session_state.messages = []
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.title = "New chat"

def load_chat(chat_id, title):
    if st.session_state.messages and st.session_state.storage:
        st.session_state.storage.save_chat(
            st.session_state.chat_id,
            st.session_state.messages,
            st.session_state.title
        )
    if st.session_state.storage:
        st.session_state.messages = st.session_state.storage.load_chat(chat_id)
    else:
        st.session_state.messages = []
    st.session_state.chat_id = chat_id
    st.session_state.title = title

# Sidebar
with st.sidebar:
    st.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
    
    # New chat button
    if st.button("+ New chat", key="new_chat", use_container_width=True):
        new_chat()
        st.rerun()
    
    # Chat history
    st.markdown('<div class="chat-history">', unsafe_allow_html=True)
    
    try:
        if st.session_state.storage:
            chats = st.session_state.storage.get_chats()
        else:
            chats = []
    except Exception as e:
        st.error(f"Error loading chats: {e}")
        chats = []
    
    for chat in chats[:20]:
        title = chat["title"][:25] + "..." if len(chat["title"]) > 25 else chat["title"]
        
        col1, col2 = st.columns([5, 1])
        with col1:
            if st.button(title, key=f"chat_{chat['id']}", use_container_width=True):
                load_chat(chat["id"], chat["title"])
                st.rerun()
        with col2:
            if st.button("🗑", key=f"del_{chat['id']}", help="Delete"):
                if st.session_state.storage:
                    st.session_state.storage.delete_chat(chat["id"])
                st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# (Removed previous manual sidebar toggle placeholder — not needed with stable layout.)

# Main content
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Messages area
st.markdown('<div class="messages-area">', unsafe_allow_html=True)

if not st.session_state.messages:
    st.markdown("""
    <div class="welcome">
        <h1>How can I help you today?</h1>
        <p>I'm ChatGPT, a large language model trained by OpenAI.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"].replace("\n", "<br>")
        
        st.markdown(f"""
        <div class="message {role}">
            <div class="message-content">{content}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-area">', unsafe_allow_html=True)
st.markdown('<div class="input-container">', unsafe_allow_html=True)

col1, col2 = st.columns([10, 1])

with col1:
    user_input = st.text_area(
        "",
        placeholder="Message ChatGPT...",
        key="user_input",
        label_visibility="collapsed",
        height=50
    )

with col2:
    send = st.button("↑", key="send", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle input
if send and user_input.strip():
    # Update title on first message
    if not st.session_state.messages:
        st.session_state.title = user_input[:30] + "..." if len(user_input) > 30 else user_input
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate response
    with st.spinner("Thinking..."):
        response = generate_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Auto-save
    if len(st.session_state.messages) % 4 == 0 and st.session_state.storage:
        st.session_state.storage.save_chat(
            st.session_state.chat_id,
            st.session_state.messages,
            st.session_state.title
        )
    
    st.session_state.user_input = ""
    st.rerun()

# Save on exit
if st.session_state.messages and st.session_state.storage:
    st.session_state.storage.save_chat(
        st.session_state.chat_id,
        st.session_state.messages,
        st.session_state.title
    )
