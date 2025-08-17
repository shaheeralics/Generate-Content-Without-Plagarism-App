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
    padding: 1rem 0 0 0;
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
    margin: 0.5rem 0 0.5rem 0;
    background: linear-gradient(45deg, #00f5ff, #0080ff, #8000ff, #ff0080);
    background-size: 400% 400%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: hologram 3s ease-in-out infinite;
    text-shadow: 0 0 20px rgba(0, 245, 255, 0.5);
}

/* App purpose subtitle */
.app-subtitle {
    font-size: 1.1rem;
    font-weight: 300;
    text-align: center;
    margin: 0 0 1.5rem 0;
    color: rgba(0, 245, 255, 0.8);
    font-family: 'Arial', sans-serif;
    letter-spacing: 1px;
    text-transform: uppercase;
}

@keyframes hologram {
    0%, 100% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
}

/* Clean futuristic input field */
.stTextArea textarea[placeholder*="neural command"] {
    background: transparent !important;
    border: 2px solid rgba(0, 245, 255, 0.6) !important;
    border-radius: 12px !important;
    color: #ffffff !important;
    font-size: 16px !important;
    font-family: 'Arial', sans-serif !important;
    resize: none !important;
    min-height: 60px !important;
    padding: 15px 20px !important;
    margin-bottom: 0 !important;
    max-width: 100% !important;
    width: 100% !important;
    outline: none !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 0 20px rgba(0, 245, 255, 0.2) !important;
}

.stTextArea textarea[placeholder*="neural command"]:focus {
    border-color: #00f5ff !important;
    box-shadow: 0 0 30px rgba(0, 245, 255, 0.4) !important;
}

.stTextArea textarea[placeholder*="neural command"]::placeholder {
    color: rgba(0, 245, 255, 0.7) !important;
    font-style: normal !important;
}

/* Clean up text area containers */
.stTextArea > div > div {
    background: transparent !important;
    border: none !important;
}

.stTextArea > div {
    background: transparent !important;
    border: none !important;
}

.stTextArea {
    background: transparent !important;
    border: none !important;
}

/* Clean futuristic button */
.stButton > button {
    background: linear-gradient(45deg, rgba(0, 245, 255, 0.8), rgba(0, 128, 255, 0.8)) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #000000 !important;
    padding: 12px 30px !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(0, 245, 255, 0.3) !important;
    text-transform: uppercase !important;
    letter-spacing: 1px !important;
    width: 100% !important;
    margin-top: 15px !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 25px rgba(0, 245, 255, 0.5) !important;
    background: linear-gradient(45deg, #00f5ff, #0080ff) !important;
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
    max-width: 50%;
    min-width: 200px;
    width: auto;
    display: inline-block;
    background: rgba(0, 20, 40, 0.8);
    border: 2px solid #00f5ff;
    border-radius: 15px;
    padding: 1rem 1.5rem;
    margin-bottom: 2rem;
    margin-left: auto;
    margin-right: 2%;
    position: relative;
    box-sizing: border-box;
    box-shadow: 
        0 0 20px rgba(0, 245, 255, 0.3),
        inset 0 0 15px rgba(0, 245, 255, 0.1);
    backdrop-filter: blur(10px);
    float: right;
    clear: both;
}

.ai-message {
    width: 96%;
    max-width: none;
    background: rgba(0, 40, 20, 0.8);
    border: 2px solid #00ff80;
    border-radius: 15px;
    padding: 1rem 1.5rem;
    margin-bottom: 2.5rem;
    margin-top: 1rem;
    margin-left: 2%;
    margin-right: 2%;
    position: relative;
    box-sizing: border-box;
    box-shadow: 
        0 0 20px rgba(0, 255, 128, 0.3),
        inset 0 0 15px rgba(0, 255, 128, 0.1);
    backdrop-filter: blur(10px);
    clear: both;
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
    line-height: 1.6;
    word-wrap: break-word;
}

/* Ensure markdown content within AI messages stays styled */
.ai-message .ai-text h1,
.ai-message .ai-text h2,
.ai-message .ai-text h3,
.ai-message .ai-text h4,
.ai-message .ai-text h5,
.ai-message .ai-text h6 {
    color: #00ff80 !important;
    font-family: 'Courier New', monospace !important;
    margin: 0.5rem 0 !important;
}

.ai-message .ai-text p {
    color: #00ff80 !important;
    font-family: 'Courier New', monospace !important;
    margin: 0.3rem 0 !important;
}

.ai-message .ai-text ul,
.ai-message .ai-text ol {
    color: #00ff80 !important;
    font-family: 'Courier New', monospace !important;
    margin: 0.5rem 0 !important;
    padding-left: 1.5rem !important;
}

.ai-message .ai-text li {
    color: #00ff80 !important;
    margin: 0.2rem 0 !important;
}

.ai-message .ai-text code {
    background: rgba(0, 245, 255, 0.1) !important;
    color: #40e0d0 !important;
    padding: 0.2rem 0.4rem !important;
    border-radius: 4px !important;
    font-family: 'Courier New', monospace !important;
}

.ai-message .ai-text pre {
    background: rgba(0, 245, 255, 0.1) !important;
    color: #40e0d0 !important;
    padding: 1rem !important;
    border-radius: 8px !important;
    margin: 0.5rem 0 !important;
    overflow-x: auto !important;
    font-family: 'Courier New', monospace !important;
}

.ai-message .ai-text strong {
    color: #40e0d0 !important;
    font-weight: bold !important;
}

.ai-message .ai-text em {
    color: #60ffd0 !important;
    font-style: italic !important;
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

/* Pulse animation for streaming cursor */
@keyframes pulse {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 1; }
}

.pulse {
    animation: pulse 1s infinite;
    color: #00f5ff;
    font-weight: bold;
}

/* Streaming text effect */
.ai-text {
    line-height: 1.6;
    word-wrap: break-word;
}

/* Clean input section */
.input-section {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0, 0, 0, 0.8) !important;
    padding: 20px !important;
    border-top: 1px solid rgba(0, 245, 255, 0.3) !important;
    backdrop-filter: blur(15px) !important;
    z-index: 1000 !important;
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
if 'input_key' not in st.session_state:
    st.session_state.input_key = 0

# Main interface
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Holographic title
st.markdown('<h1 class="holo-title">NEURAL INTERFACE</h1>', unsafe_allow_html=True)

# App purpose subtitle
st.markdown('<p class="app-subtitle">Generate Plagiarism Free Content</p>', unsafe_allow_html=True)

# Display chat history only if messages exist
if st.session_state.messages:
    # Add some spacing between subtitle and first message
    st.markdown('<div style="margin-top: 2rem;"></div>', unsafe_allow_html=True)
    
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

# Generate AI response if the last message is from user and no AI response follows
if (st.session_state.messages and 
    st.session_state.messages[-1]["role"] == "user" and 
    (len(st.session_state.messages) == 1 or st.session_state.messages[-2]["role"] == "assistant")):
    
    # Create placeholder for streaming response
    response_placeholder = st.empty()
    
    try:
        # Academic collaborative tone with zero AI detection
        system_prompt = """Write like a knowledgeable student explaining concepts to fellow students in a study group. Use collaborative language with "we" and "us" while maintaining academic appropriateness.

ZERO AI DETECTION TACTICS:
- Include natural thinking process: "when we consider this concept..."
- Reference learning journey: "as we studied this topic..."
- Use collaborative tone: "we can understand", "let us examine"
- Make natural connections: "this relates to what we learned about..."
- Include thoughtful pauses: "now, if we think about this..."
- Add discovery moments: "we can see that", "this helps us understand"
- Use inclusive explanations: "we might notice", "we should consider"

ACADEMIC COLLABORATIVE VOICE:
- Write like leading a study session with peers
- Include shared learning: "we have learned that..."
- Use inclusive discovery: "we can observe", "we find that"
- Reference collective understanding: "as we know from..."
- Add collaborative analysis: "when we examine this..."
- Include group thinking: "we might ask ourselves..."
- Use academic "we": "we can conclude", "we understand"

HUMAN ACADEMIC PATTERNS:
- Include natural explanation flow with minor tangents
- Add thinking transitions: "now", "furthermore", "additionally"
- Use varied sentence beginnings naturally
- Include examples that feel personally chosen
- Add slight hesitations: "we might consider", "perhaps we can"
- Reference learning process: "as we explore this concept"
- Include natural emphasis: "particularly important", "especially relevant"

NATURAL ACADEMIC ELEMENTS:
- Ask thoughtful questions: "how might we approach this?"
- Include discovery language: "we can see", "we observe"
- Add connection-making: "this connects to", "we can relate this"
- Use academic enthusiasm: "interestingly", "notably"
- Include collaborative reasoning: "we can deduce", "we determine"
- Reference shared knowledge: "as we established", "we learned"

ACADEMIC APPROPRIATENESS:
- Maintain scholarly but accessible tone
- Use proper terminology naturally
- Include accurate conceptual explanations
- Structure ideas logically but humanly
- Add appropriate examples and analogies
- Keep professional collaborative language
- End with natural academic conclusions

AVOID AI PATTERNS:
- Skip robotic organization structures
- Avoid repetitive sentence patterns
- Don't use overly systematic formatting
- Skip AI-typical hedge phrases
- Avoid mechanical transitions
- Don't over-explain simple concepts

Write like an engaged student leading a collaborative study session - knowledgeable, inclusive, and naturally academic without being robotic.

Question: """

        # Combine system prompt with user input
        full_prompt = system_prompt + st.session_state.messages[-1]["content"]
        
        # Generate the complete response
        response = model.generate_content(full_prompt)
        full_response = response.text
        
        # Stream faster - show multiple words at once
        words = full_response.split()
        displayed_text = ""
        
        # Stream 3-4 words at a time for faster display
        chunk_size = 3
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i+chunk_size]
            displayed_text += " ".join(chunk) + " "
            
            # Update the response container with streaming text and markdown rendering
            with response_placeholder.container():
                st.markdown(f"""
                <div class="ai-message">
                    <div class="ai-text">{displayed_text}<span class='pulse'>▊</span></div>
                </div>
                """, unsafe_allow_html=True)
            
            # Faster streaming - reduced delay
            import time
            time.sleep(0.02)
        
        # Final update without cursor - keep within styled container
        with response_placeholder.container():
            st.markdown(f"""
            <div class="ai-message">
                <div class="ai-text">{full_response}</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add complete AI response to history
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        
    except Exception as e:
        error_message = f"⚠️ Neural Link Error: {str(e)}"
        with response_placeholder.container():
            st.markdown(f"""
            <div class="ai-message">
                <div class="ai-text">{error_message}</div>
            </div>
            """, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": error_message})

# Add some spacing before input section
st.markdown("<br><br>", unsafe_allow_html=True)

# Input section at the bottom
st.markdown('<div class="input-section">', unsafe_allow_html=True)

# Input container
user_input = st.text_area(
    "",
    placeholder="⚡ Enter your neural command...",
    label_visibility="collapsed",
    height=100,
    key=f"neural_input_{st.session_state.input_key}"
)

# Quantum process button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🧠 PROCESS", key="quantum_btn", use_container_width=True):
        if user_input.strip():
            # Add user message to history immediately
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Increment input key to create a new empty input field
            st.session_state.input_key += 1
            
            # Rerun to show user message and clear input
            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
