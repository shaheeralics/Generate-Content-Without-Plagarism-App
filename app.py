import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Neural Interface",
    page_icon="🧠",
    layout="wide"
)

# Hide Streamlit default elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

/* Remove all container padding and margins */
.main .block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: none !important;
}

/* Prevent horizontal scroll */
body {
    overflow-x: hidden;
}

.stApp {
    overflow-x: hidden;
}

/* Futuristic background */
.stApp {
    background: radial-gradient(circle at 20% 50%, #120458 0%, #000000 50%, #0a0a23 100%);
    color: #ffffff;
    font-family: 'Courier New', monospace;
}

/* Main container */
.main-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1rem 0;
    margin: 0;
    width: 100%;
    position: relative;
    box-sizing: border-box;
}

/* Chat messages full width container */
.chat-messages-container {
    width: 100%;
    padding: 0 2%;
    margin: 0;
    position: relative;
    box-sizing: border-box;
}

/* Holographic title */
.holo-title {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    margin: 0.5rem 0 1rem 0;
    background: linear-gradient(45deg, #00f5ff, #0080ff, #8000ff, #ff0080);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: hologram 3s ease-in-out infinite;
    text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
}

@keyframes hologram {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Neural input container */
.neural-input {
    width: 100%;
    max-width: 800px;
    background: rgba(0, 20, 40, 0.8);
    border: 2px solid #00f5ff;
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 
        0 0 30px rgba(0, 245, 255, 0.3),
        inset 0 0 20px rgba(0, 245, 255, 0.1);
    backdrop-filter: blur(10px);
    margin-bottom: 1rem;
    position: relative;
    display: flex;
    align-items: center;
}

/* Input styling - force the text area to be contained within the box */
.neural-input .stTextArea {
    margin: 0 !important;
    padding: 0 !important;
    width: 100% !important;
    flex: 1;
}

.neural-input .stTextArea > div {
    margin: 0 !important;
    padding: 0 !important;
    background: transparent !important;
    border: none !important;
}

.neural-input .stTextArea textarea {
    background: transparent !important;
    border: none !important;
    color: #00f5ff !important;
    font-size: 18px !important;
    font-family: 'Courier New', monospace !important;
    resize: none !important;
    min-height: 100px !important;
    width: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    outline: none !important;
    box-shadow: none !important;
}

.neural-input .stTextArea textarea::placeholder {
    color: rgba(0, 245, 255, 0.5) !important;
    font-style: italic;
}

/* Quantum button */
.quantum-btn {
    background: linear-gradient(45deg, #00f5ff, #0080ff);
    border: none;
    border-radius: 50px;
    color: #000;
    padding: 1rem 3rem;
    font-size: 18px;
    font-weight: bold;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
    text-transform: uppercase;
    letter-spacing: 2px;
}

.quantum-btn:hover {
    transform: scale(1.05);
    box-shadow: 0 0 40px rgba(0, 245, 255, 0.8);
}

/* Response container */
.response-container {
    width: 100%;
    max-width: 800px;
    background: rgba(0, 40, 20, 0.8);
    border: 2px solid #00ff80;
    border-radius: 20px;
    padding: 1.5rem;
    margin-top: 1rem;
    box-shadow: 
        0 0 30px rgba(0, 255, 128, 0.3),
        inset 0 0 20px rgba(0, 255, 128, 0.1);
    backdrop-filter: blur(10px);
}

/* Message containers */
.user-message {
    width: 46%;
    max-width: none;
    background: rgba(0, 20, 40, 0.8);
    border: 2px solid #00f5ff;
    border-radius: 15px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.2rem;
    margin-left: 52%;
    margin-right: 2%;
    position: relative;
    box-sizing: border-box;
    box-shadow: 
        0 0 20px rgba(0, 245, 255, 0.3),
        inset 0 0 15px rgba(0, 245, 255, 0.1);
    backdrop-filter: blur(10px);
}

.ai-message {
    width: 96%;
    max-width: none;
    background: rgba(0, 40, 20, 0.8);
    border: 2px solid #00ff80;
    border-radius: 15px;
    padding: 1rem 1.5rem;
    margin-bottom: 1.2rem;
    margin-left: 2%;
    margin-right: 2%;
    position: relative;
    box-sizing: border-box;
    box-shadow: 
        0 0 20px rgba(0, 255, 128, 0.3),
        inset 0 0 15px rgba(0, 255, 128, 0.1);
    backdrop-filter: blur(10px);
}

.user-text {
    color: #00f5ff;
    font-size: 16px;
    line-height: 1.4;
    font-family: 'Courier New', monospace;
    text-align: right;
    margin: 0;
}

.ai-text {
    color: #00ff80;
    font-size: 16px;
    line-height: 1.4;
    font-family: 'Courier New', monospace;
    text-align: left;
    margin: 0;
}

/* Chat history container */
.chat-history {
    width: 100%;
    max-width: 100%;
    margin-bottom: 1.5rem;
}

.response-text {
    color: #00ff80;
    font-size: 16px;
    line-height: 1.6;
    font-family: 'Courier New', monospace;
}

/* Pulse animation */
@keyframes pulse {
    0%, 100% { opacity: 0.7; }
    50% { opacity: 1; }
}

.pulse {
    animation: pulse 2s infinite;
}
</style>
""", unsafe_allow_html=True)

# Configure AI
try:
    api_key = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.5-pro')
except:
    st.error("🔧 Neural Link Not Established - Configure API Key")
    st.stop()

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Main interface
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Holographic title
st.markdown('<h1 class="holo-title">NEURAL INTERFACE</h1>', unsafe_allow_html=True)

# Display chat history
if st.session_state.messages:
    st.markdown('<div class="chat-messages-container">', unsafe_allow_html=True)
    for message in st.session_state.messages:
        if message["role"] == "user":
            # Create a container for user message
            user_container = st.container()
            with user_container:
                st.markdown(f"""
                <div class="user-message">
                    <div class="user-text">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Create a container for AI message
            ai_container = st.container()
            with ai_container:
                st.markdown(f"""
                <div class="ai-message">
                    <div class="ai-text">{message["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input container - put text area INSIDE the styled div
input_container = st.container()
with input_container:
    user_input = st.text_area(
        "",
        placeholder="⚡ Enter your neural command...",
        label_visibility="collapsed",
        height=100,
        key="neural_input"
    )

# Apply neural styling to the input container
st.markdown(f"""
<style>
div[data-testid="stVerticalBlock"]:has(.stTextArea) {{
    background: rgba(0, 20, 40, 0.8) !important;
    border: 2px solid #00f5ff !important;
    border-radius: 20px !important;
    padding: 1.5rem !important;
    box-shadow: 
        0 0 30px rgba(0, 245, 255, 0.3),
        inset 0 0 20px rgba(0, 245, 255, 0.1) !important;
    backdrop-filter: blur(10px) !important;
    margin-bottom: 1rem !important;
    max-width: 800px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}}
</style>
""", unsafe_allow_html=True)

# Quantum process button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🧠 PROCESS", key="quantum_btn", use_container_width=True):
        if user_input.strip():
            # Add user message to history immediately
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Clear the input by rerunning first to show user message
            st.rerun()

# Generate AI response if the last message is from user and no AI response follows
if (st.session_state.messages and 
    st.session_state.messages[-1]["role"] == "user" and 
    (len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] == "assistant")):
    
    with st.spinner("🔮 Processing neural patterns..."):
        try:
            response = model.generate_content(st.session_state.messages[-1]["content"])
            # Add AI response to history
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.session_state.messages.append({"role": "assistant", "content": f"⚠️ Neural Link Error: {str(e)}"})
        
        # Rerun to show AI response
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)
