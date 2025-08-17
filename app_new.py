import streamlit as st
import google.generativeai as genai
import chromadb
import uuid
from datetime import datetime
import json

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize ChromaDB
@st.cache_resource
def init_vector_db():
    client = chromadb.PersistentClient(path="./chat_history")
    collection = client.get_or_create_collection(
        name="conversations",
        metadata={"hnsw:space": "cosine"}
    )
    return client, collection

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if 'db_client' not in st.session_state:
    st.session_state.db_client, st.session_state.collection = init_vector_db()

# Custom CSS for ChatGPT-like interface
st.markdown("""
<style>
    /* Main container */
    .main {
        background-color: #212121;
        color: #ffffff;
        padding: 0;
    }
    
    /* Hide streamlit header */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Top bar styling */
    .top-bar {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 60px;
        background: #343541;
        border-bottom: 1px solid #565869;
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 0 20px;
    }
    
    .app-title {
        color: #ffffff;
        font-size: 18px;
        font-weight: 600;
        margin: 0;
    }
    
    .new-chat-btn {
        position: absolute;
        left: 20px;
        background: #10a37f;
        color: white;
        border: none;
        padding: 8px 16px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
    }
    
    .new-chat-btn:hover {
        background: #0d8c6f;
    }
    
    /* Chat container */
    .chat-container {
        margin-top: 80px;
        max-width: 768px;
        margin-left: auto;
        margin-right: auto;
        padding: 20px;
        min-height: calc(100vh - 200px);
    }
    
    /* Message styling */
    .user-message {
        background: #343541;
        padding: 20px;
        margin: 20px 0;
        border-radius: 8px;
        border-left: 4px solid #10a37f;
    }
    
    .assistant-message {
        background: #444654;
        padding: 20px;
        margin: 20px 0;
        border-radius: 8px;
        border-left: 4px solid #9a6aff;
    }
    
    .message-header {
        font-weight: 600;
        margin-bottom: 10px;
        color: #ffffff;
        font-size: 14px;
    }
    
    .message-content {
        color: #ececf1;
        line-height: 1.6;
        font-size: 16px;
    }
    
    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #343541;
        border-top: 1px solid #565869;
        padding: 20px;
    }
    
    .input-wrapper {
        max-width: 768px;
        margin: 0 auto;
        position: relative;
    }
    
    /* Hide default streamlit elements */
    .stTextArea > div > div > textarea {
        background: #40414f !important;
        border: 1px solid #565869 !important;
        border-radius: 12px !important;
        color: #ececf1 !important;
        font-size: 16px !important;
        resize: none !important;
        padding: 12px 50px 12px 16px !important;
        min-height: 48px !important;
        max-height: 200px !important;
    }
    
    .stTextArea > div > div > textarea:focus {
        border-color: #10a37f !important;
        box-shadow: 0 0 0 2px rgba(16, 163, 127, 0.2) !important;
        outline: none !important;
    }
    
    /* Send button */
    .stButton > button {
        background: #10a37f !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 8px 16px !important;
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
    
    /* Welcome message */
    .welcome-container {
        text-align: center;
        padding: 60px 20px;
        color: #ececf1;
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 16px;
        color: #ffffff;
    }
    
    .welcome-subtitle {
        font-size: 16px;
        color: #8e8ea0;
        margin-bottom: 40px;
    }
    
    /* Loading animation */
    .typing-indicator {
        display: inline-block;
        color: #8e8ea0;
        font-style: italic;
    }
    
    .dot {
        animation: typing 1.4s infinite;
        margin: 0 2px;
    }
    
    .dot:nth-child(2) { animation-delay: 0.2s; }
    .dot:nth-child(3) { animation-delay: 0.4s; }
    
    @keyframes typing {
        0%, 60%, 100% { opacity: 0.3; }
        30% { opacity: 1; }
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #212121;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #565869;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #6c6d7a;
    }
</style>
""", unsafe_allow_html=True)

# Configure Gemini API
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-pro')

def save_conversation_to_db(chat_id, messages):
    """Save conversation to vector database"""
    try:
        conversation_text = ""
        for msg in messages:
            conversation_text += f"{msg['role']}: {msg['content']}\n"
        
        # Create metadata
        metadata = {
            "chat_id": chat_id,
            "timestamp": datetime.now().isoformat(),
            "message_count": len(messages)
        }
        
        # Save to vector database
        st.session_state.collection.add(
            documents=[conversation_text],
            metadatas=[metadata],
            ids=[chat_id]
        )
    except Exception as e:
        st.error(f"Error saving conversation: {e}")

def rewrite_content_ai(text):
    """AI-driven content rewriting using Gemini Pro"""
    prompt = f"""
    You are an expert content rewriter. Rewrite the following text while:
    1. Maintaining the original meaning
    2. Using different vocabulary and sentence structures
    3. Making it natural and human-like
    4. Avoiding plagiarism detection
    5. Improving clarity and readability

    Text: {text}

    Provide a completely rewritten version:
    """
    
    response = model.generate_content(prompt)
    return response.text

def start_new_chat():
    """Start a new chat session"""
    # Save current conversation if it exists
    if st.session_state.messages:
        save_conversation_to_db(st.session_state.chat_id, st.session_state.messages)
    
    # Reset session
    st.session_state.messages = []
    st.session_state.chat_id = str(uuid.uuid4())

# Top bar
st.markdown("""
<div class="top-bar">
    <button class="new-chat-btn" onclick="window.location.reload()">+ New Chat</button>
    <h1 class="app-title">AI Content Assistant</h1>
</div>
""", unsafe_allow_html=True)

# Main chat interface
chat_container = st.container()

with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message if no conversation
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">How can I help you today?</h1>
            <p class="welcome-subtitle">I can help you rewrite content, answer questions, and assist with various tasks.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">You</div>
                <div class="message-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">Assistant</div>
                <div class="message-content">{message["content"]}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)

# Create columns for input and button
col1, col2 = st.columns([10, 1])

with col1:
    user_input = st.text_area(
        "Message AI Assistant...",
        key="user_input",
        placeholder="Type your message here...",
        label_visibility="collapsed",
        height=48
    )

with col2:
    send_button = st.button("↑", key="send_btn")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle user input
if send_button and user_input.strip():
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show typing indicator
    with st.spinner(""):
        st.markdown("""
        <div class="assistant-message">
            <div class="message-header">Assistant</div>
            <div class="message-content">
                <span class="typing-indicator">
                    Thinking<span class="dot">.</span><span class="dot">.</span><span class="dot">.</span>
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        try:
            # Generate response
            response = rewrite_content_ai(user_input)
            
            # Add assistant response
            st.session_state.messages.append({"role": "assistant", "content": response})
            
            # Auto-save conversation periodically
            if len(st.session_state.messages) % 4 == 0:  # Save every 4 messages
                save_conversation_to_db(st.session_state.chat_id, st.session_state.messages)
            
        except Exception as e:
            error_message = f"I apologize, but I encountered an error: {str(e)}. Please try again."
            st.session_state.messages.append({"role": "assistant", "content": error_message})
    
    # Clear input and rerun
    st.session_state.user_input = ""
    st.rerun()
