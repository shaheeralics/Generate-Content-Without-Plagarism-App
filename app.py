import streamlit as st
import google.generativeai as genai

# Page configuration
st.set_page_config(
    page_title="Neural Interface",
    page_icon="🧠",
    layout="centered"
)

# Hide Streamlit default elements
st.markdown("""
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.stDeployButton {display: none;}

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
    padding: 1rem;
    margin: 0;
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
}

/* Input styling */
.stTextArea textarea {
    background: transparent !important;
    border: none !important;
    color: #00f5ff !important;
    font-size: 18px !important;
    font-family: 'Courier New', monospace !important;
    resize: none !important;
    min-height: 100px !important;
}

.stTextArea textarea::placeholder {
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
if 'current_response' not in st.session_state:
    st.session_state.current_response = ""

# Main interface
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Holographic title
st.markdown('<h1 class="holo-title">NEURAL INTERFACE</h1>', unsafe_allow_html=True)

# Input container
st.markdown('<div class="neural-input">', unsafe_allow_html=True)
user_input = st.text_area(
    "",
    placeholder="⚡ Enter your neural command...",
    label_visibility="collapsed",
    height=100,
    key="neural_input"
)
st.markdown('</div>', unsafe_allow_html=True)

# Quantum process button
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🧠 PROCESS", key="quantum_btn", use_container_width=True):
        if user_input.strip():
            with st.spinner("🔮 Processing neural patterns..."):
                try:
                    response = model.generate_content(user_input)
                    st.session_state.current_response = response.text
                except Exception as e:
                    st.session_state.current_response = f"⚠️ Neural Link Error: {str(e)}"

# Display response
if st.session_state.current_response:
    st.markdown('<div class="response-container pulse">', unsafe_allow_html=True)
    st.markdown(f'<div class="response-text">{st.session_state.current_response}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
