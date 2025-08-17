import streamlit as st
import google.generativeai as genai
import uuid
from datetime import datetime, timedelta
import json
from chat_history import ChatHistoryManager
from utils import AIResponseHandler, ChatUtils, ExportManager, AdvancedSearch, get_response_stats

# Page configuration
st.set_page_config(
    page_title="AI Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize chat history manager
@st.cache_resource
def init_chat_manager():
    return ChatHistoryManager()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'chat_id' not in st.session_state:
    st.session_state.chat_id = str(uuid.uuid4())
if 'chat_manager' not in st.session_state:
    st.session_state.chat_manager = init_chat_manager()
if 'current_chat_title' not in st.session_state:
    st.session_state.current_chat_title = "New Chat"
if 'show_stats' not in st.session_state:
    st.session_state.show_stats = False
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = True

# Custom CSS for ChatGPT-like interface
def get_css_theme():
    if st.session_state.dark_mode:
        return """
        <style>
            /* Dark theme */
            .main {
                background-color: #212121;
                color: #ffffff;
                padding: 0;
            }
            
            .css-1d391kg {
                background-color: #202123;
                border-right: 1px solid #565869;
            }
            
            .user-message {
                background: #343541;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 4px solid #10a37f;
                max-width: 80%;
                margin-left: auto;
            }
            
            .assistant-message {
                background: #444654;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 4px solid #9a6aff;
                max-width: 80%;
            }
            
            .top-bar {
                background: #343541;
                border-bottom: 1px solid #565869;
            }
            
            .input-container {
                background: #343541;
                border-top: 1px solid #565869;
            }
        </style>
        """
    else:
        return """
        <style>
            /* Light theme */
            .main {
                background-color: #ffffff;
                color: #000000;
                padding: 0;
            }
            
            .css-1d391kg {
                background-color: #f7f7f8;
                border-right: 1px solid #d1d5db;
            }
            
            .user-message {
                background: #f0f9ff;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 4px solid #0ea5e9;
                max-width: 80%;
                margin-left: auto;
            }
            
            .assistant-message {
                background: #f9fafb;
                padding: 20px;
                margin: 20px 0;
                border-radius: 8px;
                border-left: 4px solid #8b5cf6;
                max-width: 80%;
            }
            
            .top-bar {
                background: #ffffff;
                border-bottom: 1px solid #d1d5db;
            }
            
            .input-container {
                background: #ffffff;
                border-top: 1px solid #d1d5db;
            }
        </style>
        """

st.markdown(get_css_theme(), unsafe_allow_html=True)

# Common CSS
st.markdown("""
<style>
    /* Hide streamlit header */
    header[data-testid="stHeader"] {
        display: none;
    }
    
    /* Top bar styling */
    .top-bar {
        position: fixed;
        top: 0;
        left: 300px;
        right: 0;
        height: 60px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        z-index: 1000;
        padding: 0 20px;
    }
    
    .app-title {
        font-size: 18px;
        font-weight: 600;
        margin: 0;
    }
    
    .top-controls {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .control-btn {
        background: #10a37f;
        color: white;
        border: none;
        padding: 6px 12px;
        border-radius: 6px;
        cursor: pointer;
        font-size: 12px;
        font-weight: 500;
    }
    
    .control-btn:hover {
        background: #0d8c6f;
    }
    
    /* Chat container */
    .chat-container {
        margin-top: 80px;
        margin-left: 0px;
        max-width: 100%;
        padding: 20px;
        min-height: calc(100vh - 200px);
    }
    
    .message-header {
        font-weight: 600;
        margin-bottom: 10px;
        font-size: 14px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .message-content {
        line-height: 1.6;
        font-size: 16px;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    
    .message-stats {
        font-size: 11px;
        opacity: 0.7;
        margin-top: 8px;
        font-style: italic;
    }
    
    /* Input area */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 300px;
        right: 0;
        padding: 20px;
    }
    
    .input-wrapper {
        max-width: 768px;
        margin: 0 auto;
        position: relative;
    }
    
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
    }
    
    .welcome-title {
        font-size: 32px;
        font-weight: 600;
        margin-bottom: 16px;
    }
    
    .welcome-subtitle {
        font-size: 16px;
        opacity: 0.7;
        margin-bottom: 40px;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        max-width: 800px;
        margin: 0 auto;
    }
    
    .feature-card {
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #565869;
        background: rgba(255, 255, 255, 0.05);
        text-align: center;
    }
    
    .feature-icon {
        font-size: 32px;
        margin-bottom: 12px;
    }
    
    .feature-title {
        font-weight: 600;
        margin-bottom: 8px;
    }
    
    .feature-desc {
        font-size: 14px;
        opacity: 0.8;
    }
    
    /* Responsive */
    @media (max-width: 768px) {
        .top-bar {
            left: 0;
        }
        .input-container {
            left: 0;
        }
        .chat-container {
            margin-left: 0;
        }
    }
    
    /* Sidebar styling */
    .chat-item {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid #565869;
        border-radius: 8px;
        padding: 12px;
        margin: 8px 0;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .chat-item:hover {
        background: rgba(255, 255, 255, 0.1);
        border-color: #10a37f;
    }
    
    .export-menu {
        background: #343541;
        border: 1px solid #565869;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Configure Gemini API
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
except Exception as e:
    st.error("⚠️ Please configure your Gemini API key in .streamlit/secrets.toml")
    st.stop()

def generate_ai_response(text):
    """Generate AI response with content type detection"""
    try:
        content_type = AIResponseHandler.detect_content_type(text)
        prompt = AIResponseHandler.get_specialized_prompt(content_type, text)
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"I apologize, but I encountered an error: {str(e)}. Please try again."

def start_new_chat():
    """Start a new chat session"""
    if st.session_state.messages:
        st.session_state.chat_manager.save_conversation(
            st.session_state.chat_id, 
            st.session_state.messages,
            st.session_state.current_chat_title
        )
    
    st.session_state.messages = []
    st.session_state.chat_id = str(uuid.uuid4())
    st.session_state.current_chat_title = "New Chat"

def load_chat(chat_id):
    """Load a specific chat"""
    messages, metadata = st.session_state.chat_manager.load_conversation(chat_id)
    if messages:
        if st.session_state.messages:
            st.session_state.chat_manager.save_conversation(
                st.session_state.chat_id,
                st.session_state.messages,
                st.session_state.current_chat_title
            )
        
        st.session_state.messages = messages
        st.session_state.chat_id = chat_id
        st.session_state.current_chat_title = metadata.get('title', 'Untitled Chat')

# Sidebar for chat history and controls
with st.sidebar:
    st.markdown("### 🤖 AI Assistant")
    
    # Theme toggle
    if st.button("🌓 Toggle Theme", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()
    
    # Stats toggle
    if st.button("📊 Toggle Stats", use_container_width=True):
        st.session_state.show_stats = not st.session_state.show_stats
        st.rerun()
    
    st.markdown("---")
    
    # New chat button
    if st.button("➕ New Chat", key="new_chat", use_container_width=True):
        start_new_chat()
        st.rerun()
    
    # Search and filters
    st.markdown("### 🔍 Search & Filter")
    search_query = st.text_input("Search conversations...", key="search_box")
    
    # Advanced search options
    with st.expander("🔧 Advanced Search"):
        search_type = st.selectbox("Search Type", ["Content", "Date Range", "Message Count"])
        
        if search_type == "Date Range":
            start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
            end_date = st.date_input("End Date", datetime.now())
            if st.button("Search by Date"):
                conversations = AdvancedSearch.search_by_date_range(
                    st.session_state.chat_manager, start_date, end_date
                )
            else:
                conversations = st.session_state.chat_manager.get_all_conversations()
        
        elif search_type == "Message Count":
            min_msgs = st.number_input("Min Messages", min_value=0, value=0)
            max_msgs = st.number_input("Max Messages", min_value=1, value=100)
            if st.button("Search by Count"):
                conversations = AdvancedSearch.search_by_message_count(
                    st.session_state.chat_manager, min_msgs, max_msgs
                )
            else:
                conversations = st.session_state.chat_manager.get_all_conversations()
        else:
            if search_query:
                conversations = st.session_state.chat_manager.search_conversations(search_query)
            else:
                conversations = st.session_state.chat_manager.get_all_conversations()
    
    # Get conversations based on search
    if not 'conversations' in locals():
        if search_query:
            conversations = st.session_state.chat_manager.search_conversations(search_query)
        else:
            conversations = st.session_state.chat_manager.get_all_conversations()
    
    # Display conversations
    st.markdown("### 💬 Chat History")
    for conv in conversations[:20]:
        chat_preview = conv['title'][:35] + ("..." if len(conv['title']) > 35 else "")
        
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(
                f"{chat_preview}", 
                key=f"chat_{conv['chat_id']}", 
                help=f"Messages: {conv['message_count']} | {ChatUtils.format_timestamp(conv['timestamp'])}"
            ):
                load_chat(conv['chat_id'])
                st.rerun()
        
        with col2:
            if st.button("🗑️", key=f"delete_{conv['chat_id']}", help="Delete chat"):
                st.session_state.chat_manager.delete_conversation(conv['chat_id'])
                st.rerun()
    
    # Export options
    if st.session_state.messages:
        st.markdown("---")
        st.markdown("### 📤 Export Chat")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📄 Text", help="Export as plain text"):
                metadata = {'title': st.session_state.current_chat_title, 'created_date': datetime.now().strftime('%Y-%m-%d'), 'created_time': datetime.now().strftime('%H:%M')}
                text_export = ExportManager.export_to_text(st.session_state.messages, metadata)
                st.download_button(
                    "Download TXT",
                    text_export,
                    f"chat_{st.session_state.chat_id}.txt",
                    "text/plain"
                )
        
        with col2:
            if st.button("📋 JSON", help="Export as JSON"):
                metadata = {'title': st.session_state.current_chat_title, 'created_date': datetime.now().strftime('%Y-%m-%d'), 'created_time': datetime.now().strftime('%H:%M')}
                json_export = ExportManager.export_to_json(st.session_state.messages, metadata)
                st.download_button(
                    "Download JSON",
                    json_export,
                    f"chat_{st.session_state.chat_id}.json",
                    "application/json"
                )
    
    # Footer stats
    st.markdown("---")
    st.markdown("**💾 Auto-save enabled**")
    st.markdown(f"**📊 Total chats:** {len(conversations)}")
    if st.session_state.messages:
        st.markdown(f"**💬 Current messages:** {len(st.session_state.messages)}")

# Main content area
main_col = st.container()

with main_col:
    # Top bar
    st.markdown(f"""
    <div class="top-bar">
        <h1 class="app-title">{st.session_state.current_chat_title}</h1>
        <div class="top-controls">
            <span style="font-size: 12px; opacity: 0.7;">
                {f"Theme: {'Dark' if st.session_state.dark_mode else 'Light'}" + 
                 f" | Stats: {'On' if st.session_state.show_stats else 'Off'}"}
            </span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat container
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # Welcome message if no conversation
    if not st.session_state.messages:
        st.markdown("""
        <div class="welcome-container">
            <h1 class="welcome-title">How can I help you today?</h1>
            <p class="welcome-subtitle">I'm your AI assistant, ready to help with content rewriting, questions, and various tasks.</p>
            
            <div class="feature-grid">
                <div class="feature-card">
                    <div class="feature-icon">✍️</div>
                    <div class="feature-title">Content Rewriting</div>
                    <div class="feature-desc">Rewrite text while maintaining meaning and avoiding plagiarism</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">📝</div>
                    <div class="feature-title">Summarization</div>
                    <div class="feature-desc">Create concise summaries of long texts</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">🎯</div>
                    <div class="feature-title">Content Improvement</div>
                    <div class="feature-desc">Enhance clarity, grammar, and readability</div>
                </div>
                <div class="feature-card">
                    <div class="feature-icon">❓</div>
                    <div class="feature-title">Q&A Assistant</div>
                    <div class="feature-desc">Get detailed explanations and answers</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Display chat messages
    for i, message in enumerate(st.session_state.messages):
        if message["role"] == "user":
            st.markdown(f"""
            <div class="user-message">
                <div class="message-header">
                    <span>You</span>
                    <span style="font-size: 11px; opacity: 0.6;">#{i+1}</span>
                </div>
                <div class="message-content">{ChatUtils.clean_text(message["content"])}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            content = ChatUtils.clean_text(message["content"])
            stats_html = ""
            
            if st.session_state.show_stats:
                stats = get_response_stats(message["content"])
                stats_html = f"""
                <div class="message-stats">
                    📊 {stats['word_count']} words • {stats['character_count']} chars • {stats['reading_time']}
                </div>
                """
            
            st.markdown(f"""
            <div class="assistant-message">
                <div class="message-header">
                    <span>Assistant</span>
                    <span style="font-size: 11px; opacity: 0.6;">#{i+1}</span>
                </div>
                <div class="message-content">{content}</div>
                {stats_html}
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-container">', unsafe_allow_html=True)
st.markdown('<div class="input-wrapper">', unsafe_allow_html=True)

col1, col2 = st.columns([10, 1])

with col1:
    user_input = st.text_area(
        "Message AI Assistant...",
        key="user_input",
        placeholder="Type your message here... (e.g., 'Rewrite this text:', 'Summarize:', 'Explain:')",
        label_visibility="collapsed",
        height=48
    )

with col2:
    send_button = st.button("↑", key="send_btn")

st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Handle user input
if send_button and user_input.strip():
    # Update chat title on first message
    if not st.session_state.messages:
        st.session_state.current_chat_title = st.session_state.chat_manager.generate_title(user_input)
    
    # Add user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Generate and add assistant response
    with st.spinner("🤔 Thinking..."):
        response = generate_ai_response(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
    
    # Auto-save conversation
    if len(st.session_state.messages) % 4 == 0:
        st.session_state.chat_manager.save_conversation(
            st.session_state.chat_id,
            st.session_state.messages,
            st.session_state.current_chat_title
        )
    
    # Clear input and rerun
    st.session_state.user_input = ""
    st.rerun()

# Auto-save on app interaction
if st.session_state.messages and len(st.session_state.messages) > 0:
    st.session_state.chat_manager.save_conversation(
        st.session_state.chat_id,
        st.session_state.messages,
        st.session_state.current_chat_title
    )
