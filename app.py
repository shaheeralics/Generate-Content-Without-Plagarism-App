import streamlit as st
import google.generativeai as genai
import os

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="NeuralWrite AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- Futuristic CSS ---
st.markdown(
    """
    <style>
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display:none;}
    
    /* Custom background and fonts */
    .stApp {
        background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 25%, #16213e 50%, #0f3460 75%, #533483 100%);
        font-family: 'Courier New', 'Monaco', 'Menlo', monospace;
        color: #00ff88;
    }
    
    /* Neon title */
    .neon-title {
        font-size: 3.5em;
        text-align: center;
        color: #00ff88;
        text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88;
        margin-bottom: 20px;
        font-weight: bold;
        letter-spacing: 3px;
    }
    
    .subtitle {
        text-align: center;
        color: #64ffda;
        font-size: 1.3em;
        margin-bottom: 50px;
        opacity: 0.9;
    }
    
    /* Section spacing */
    .stMarkdown h3 {
        margin-top: 30px !important;
        margin-bottom: 20px !important;
        color: #00ff88;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        border-bottom: 2px solid #00ff88;
        padding-bottom: 10px;
    }
    
    /* Input styling */
    .stTextInput, .stTextArea {
        margin: 20px 0 !important;
    }
    
    /* Remove any wrapper scrolling */
    .stTextArea > div {
        overflow: visible !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(0, 20, 40, 0.9);
        border: 2px solid #00ff88;
        border-radius: 15px;
        color: #00ff88;
        font-size: 16px;
        padding: 15px;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
        resize: vertical;
        overflow: auto !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #64ffda;
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
        outline: none;
    }
    
    /* Text area specific styling */
    .stTextArea > div > div > textarea {
        min-height: 120px;
        max-height: 200px;
        line-height: 1.5;
        word-wrap: break-word;
        white-space: pre-wrap;
    }
    
    /* Custom scrollbar for text area only */
    .stTextArea > div > div > textarea::-webkit-scrollbar {
        width: 8px;
    }
    
    .stTextArea > div > div > textarea::-webkit-scrollbar-track {
        background: rgba(0, 20, 40, 0.5);
        border-radius: 10px;
    }
    
    .stTextArea > div > div > textarea::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00ff88, #64ffda);
        border-radius: 10px;
    }
    
    .stTextArea > div > div > textarea::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(180deg, #64ffda, #00ff88);
    }
    
    /* Slider styling */
    .stSlider {
        margin: 25px 0 !important;
        padding: 10px 0;
    }
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00ff88, #64ffda);
    }
    
    .stSlider > div > div > div > div {
        background: #00ff88;
        border: 2px solid #64ffda;
    }
    
    /* Button styling */
    .stButton {
        margin: 30px 0 !important;
        text-align: center;
    }
    
    .stButton > button {
        background: linear-gradient(45deg, #00ff88, #64ffda);
        color: #000;
        border: none;
        border-radius: 25px;
        font-size: 18px;
        font-weight: bold;
        padding: 15px 40px;
        box-shadow: 0 0 30px rgba(0, 255, 136, 0.6);
        transition: all 0.3s ease;
        font-family: 'Courier New', monospace;
        margin: 10px 0;
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 50px rgba(0, 255, 136, 0.8);
    }
    
    /* Download button */
    .stDownloadButton {
        margin: 20px 0 !important;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(45deg, #ff6b6b, #feca57);
        color: #000;
        border: none;
        border-radius: 20px;
        font-size: 16px;
        font-weight: bold;
        padding: 12px 30px;
        box-shadow: 0 0 25px rgba(255, 107, 107, 0.5);
        font-family: 'Courier New', monospace;
    }
    
    /* Progress indicators */
    .step-indicator {
        background: rgba(0, 255, 136, 0.1);
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0;
        color: #00ff88;
        font-family: 'Courier New', monospace;
    }
    
    /* Output container */
    .output-container {
        background: rgba(0, 20, 40, 0.8);
        border: 2px solid #64ffda;
        border-radius: 15px;
        padding: 30px;
        margin: 30px 0;
        box-shadow: 0 0 30px rgba(100, 255, 218, 0.2);
    }
    
    /* Markdown content */
    .stMarkdown {
        color: #e0e0e0;
        font-family: 'Georgia', serif;
        line-height: 1.8;
        margin: 15px 0 !important;
    }
    
    .stMarkdown h3 {
        color: #00ff88;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        border-bottom: 2px solid #00ff88;
        padding-bottom: 10px;
        margin-top: 30px !important;
        margin-bottom: 20px !important;
    }
    
    .stMarkdown h4 {
        color: #64ffda;
        margin-top: 25px !important;
        margin-bottom: 15px !important;
    }
    
    .stMarkdown p {
        margin: 15px 0 !important;
    }
    
    .stMarkdown ul, .stMarkdown ol {
        margin: 15px 0 !important;
        padding-left: 20px;
    }
    
    .stMarkdown li {
        margin: 8px 0 !important;
    }
    
    .stMarkdown code {
        background: rgba(0, 255, 136, 0.1);
        color: #00ff88;
        padding: 2px 6px;
        border-radius: 5px;
        margin: 0 2px;
    }
    
    .stMarkdown pre {
        background: rgba(0, 20, 40, 0.9);
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 15px;
        margin: 20px 0 !important;
    }
    
    .stMarkdown hr {
        border: 1px solid #00ff88;
        margin: 30px 0 !important;
    }
    
    /* Code block styling */
    .stCode {
        margin: 20px 0 !important;
    }
    
    /* Column spacing */
    .stColumn {
        padding: 0 10px;
    }
    
    /* Spinner styling */
    .stSpinner {
        color: #00ff88;
        margin: 20px 0 !important;
    }
    
    /* Warning and error messages */
    .stAlert {
        background: rgba(255, 107, 107, 0.1);
        border: 1px solid #ff6b6b;
        color: #ff6b6b;
        border-radius: 10px;
    }
    
    /* Footer */
    .custom-footer {
        text-align: center;
        margin-top: 50px;
        padding: 20px;
        color: #64ffda;
        font-size: 14px;
        border-top: 1px solid #00ff88;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Gemini API Setup ---
try:
    # Get API key from Streamlit secrets (works both locally and on Streamlit Cloud)
    api_key = st.secrets["GEMINI_API_KEY"]
    
    if not api_key:
        st.error("⚠️ API Key is empty. Please check your Streamlit secrets configuration.")
        st.stop()
    
    genai.configure(api_key=api_key)
    
    # Try different model names that are more likely to work
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
    except:
        try:
            model = genai.GenerativeModel('gemini-pro')
        except:
            model = genai.GenerativeModel('gemini-1.0-pro')
    
except KeyError:
    st.error("⚠️ GEMINI_API_KEY not found in Streamlit secrets.")
    st.info("📝 Please add GEMINI_API_KEY to your Streamlit secrets (App settings → Secrets)")
    st.stop()
except Exception as e:
    st.error(f"❌ API Setup Error: {e}")
    st.info("💡 Please verify your API key is valid and has access to Gemini models")
    st.stop()

# --- AI-Driven Rewriting Pipeline ---
def ai_synonym_replacement(text, intensity):
    """Step 1: AI replaces words with synonyms based on intensity"""
    prompt = f"""
    You are helping someone rewrite text to avoid plagiarism. Replace about {int(intensity * 100)}% of the key words with natural synonyms, but make it sound like a human wrote it, not an AI.
    
    Important:
    - Use everyday language, not fancy academic words
    - Keep the same casual/formal tone as the original
    - Don't make it sound robotic or perfect
    - Keep all the same ideas and facts
    - Make small, natural word choices
    
    Text: {text}
    
    Just give me the rewritten version:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return text

def ai_paraphrasing(text):
    """Step 2: AI paraphrases for better flow"""
    prompt = f"""
    Rewrite this text so it flows better and sounds more natural, like how a real person would explain it to a friend. Don't make it sound like a robot or textbook.
    
    Keep it:
    - Natural and conversational 
    - Same length roughly
    - Same information and facts
    - Easy to read
    - Human-like, not AI-perfect
    
    Text: {text}
    
    Just rewrite it naturally:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return text

def ai_humanization(text):
    """Step 3: AI adds natural human-like elements"""
    prompt = f"""
    Make this text sound like it was written by a real human, not an AI. Add some natural imperfections and human touches.
    
    Add things like:
    - Natural transitions that humans use
    - Slight variations in sentence length
    - More casual, conversational tone
    - Less perfect structure
    - Human-like explanations
    
    Don't:
    - Make it sound robotic or too polished
    - Use overly formal language
    - Make every sentence the same length
    - Add unnecessary complexity
    
    Text: {text}
    
    Make it sound human:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return text

# --- Streamlit UI ---
# Title and header
st.markdown(
    """
    <div class="neon-title">⚡ NEURALWRITE AI ⚡</div>
    <div class="subtitle">Advanced Neural Content Rewriting System</div>
    """, 
    unsafe_allow_html=True
)

# Create columns for better layout
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### Input")
    prompt = st.text_area("", placeholder="Enter your content prompt here...", height=120, key="prompt_input", help="Describe what you want to generate. You can write multiple lines.")
    
    st.markdown("### Select Intensity")
    intensity = st.slider("Rewrite Intensity Level", 0.0, 1.0, 0.3, 0.05, help="Controls how aggressively the AI rewrites content")
    
    st.markdown("### Generate AI Free Response")
    generate_button = st.button("🔥 GENERATE & REWRITE 🔥", key="main_button")

if generate_button and prompt:
    with st.spinner("Generating content with Gemini Pro..."):
        try:
            # Enhanced prompt for more human-like initial generation
            enhanced_prompt = f"""
            Write about: {prompt}
            
            Write this in a natural, human way - like you're explaining it to someone who's interested but not an expert. Make it informative but conversational. Don't make it sound like a robot or textbook wrote it.
            
            Make it:
            - Natural and engaging
            - Easy to understand  
            - Well-structured but not overly formal
            - Informative but not robotic
            """
            
            response = model.generate_content(enhanced_prompt)
            ai_text = response.text.strip()
        except Exception as e:
            st.error(f"Error generating content: {e}")
            ai_text = ""
    if ai_text:
        with st.spinner("⚡ Initializing Neural Networks..."):
            # Step 1: AI Synonym Replacement
            st.markdown('<div class="step-indicator">🧠 PHASE 1: Neural Synonym Processing...</div>', unsafe_allow_html=True)
            rewritten = ai_synonym_replacement(ai_text, intensity)
            
            # Step 2: AI Paraphrasing
            st.markdown('<div class="step-indicator">🔄 PHASE 2: Contextual Paraphrasing...</div>', unsafe_allow_html=True)
            rewritten = ai_paraphrasing(rewritten)
            
            # Step 3: AI Humanization
            st.markdown('<div class="step-indicator">✨ PHASE 3: Human-Like Enhancement...</div>', unsafe_allow_html=True)
            rewritten = ai_humanization(rewritten)
        # Display the output directly as markdown (Gemini already provides markdown)
        st.markdown('<div class="output-container">', unsafe_allow_html=True)
        st.markdown("### 📝 Original Prompt")
        st.code(prompt, language="text")
        st.markdown("---")
        st.markdown("### ✨ Rewritten Content")
        st.markdown(rewritten)  # Simply display the AI output as markdown
        st.markdown("---")
        st.markdown("### 🎯 Processing Summary")
        st.markdown(f"""
        - **Generated by:** Gemini 2.5 Pro AI Model
        - **Processing Steps:** 3-Phase Neural Enhancement
        - **Rewrite Intensity:** {int(intensity * 100)}%
        - **Content Type:** Human-like, Natural Language
        """)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download section
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.download_button(
                label="📥 DOWNLOAD CONTENT",
                data=rewritten,
                file_name="neuralwrite_output.txt",
                mime="text/plain",
                key="download_btn"
            )
    else:
        st.markdown('<div class="step-indicator">⚠️ ERROR: Neural networks failed to generate content. Please try again.</div>', unsafe_allow_html=True)

elif generate_button and not prompt:
    st.markdown('<div class="step-indicator">⚠️ WARNING: Please enter a prompt to begin neural processing.</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="custom-footer">
        <div style="font-size: 16px; margin-bottom: 10px;">⚡ NEURALWRITE AI ⚡</div>
        <div>Powered by Advanced Neural Networks | Gemini 2.5 Pro | 2025</div>
        <div style="margin-top: 10px; font-size: 12px; opacity: 0.7;">
            🔬 Research-Grade Content Generation | 🛡️ Privacy Protected | 🚀 Lightning Fast
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
