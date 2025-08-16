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
    
    /* Futuristic container */
    .main-container {
        background: rgba(0, 0, 0, 0.8);
        border: 2px solid #00ff88;
        border-radius: 20px;
        padding: 30px;
        margin: 20px auto;
        max-width: 1200px;
        box-shadow: 0 0 50px rgba(0, 255, 136, 0.3);
        backdrop-filter: blur(10px);
    }
    
    /* Neon title */
    .neon-title {
        font-size: 3.5em;
        text-align: center;
        color: #00ff88;
        text-shadow: 0 0 10px #00ff88, 0 0 20px #00ff88, 0 0 30px #00ff88;
        margin-bottom: 10px;
        font-weight: bold;
        letter-spacing: 3px;
    }
    
    .subtitle {
        text-align: center;
        color: #64ffda;
        font-size: 1.3em;
        margin-bottom: 40px;
        opacity: 0.9;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: rgba(0, 20, 40, 0.9);
        border: 2px solid #00ff88;
        border-radius: 15px;
        color: #00ff88;
        font-size: 16px;
        padding: 15px;
        font-family: 'Courier New', monospace;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #64ffda;
        box-shadow: 0 0 20px rgba(100, 255, 218, 0.5);
    }
    
    /* Slider styling */
    .stSlider > div > div > div {
        background: linear-gradient(90deg, #00ff88, #64ffda);
    }
    
    .stSlider > div > div > div > div {
        background: #00ff88;
        border: 2px solid #64ffda;
    }
    
    /* Button styling */
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
    }
    
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 50px rgba(0, 255, 136, 0.8);
    }
    
    /* Download button */
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
        padding: 10px;
        margin: 10px 0;
        color: #00ff88;
        font-family: 'Courier New', monospace;
    }
    
    /* Output container */
    .output-container {
        background: rgba(0, 20, 40, 0.8);
        border: 2px solid #64ffda;
        border-radius: 15px;
        padding: 25px;
        margin: 20px 0;
        box-shadow: 0 0 30px rgba(100, 255, 218, 0.2);
    }
    
    /* Markdown content */
    .stMarkdown {
        color: #e0e0e0;
        font-family: 'Georgia', serif;
        line-height: 1.8;
    }
    
    .stMarkdown h3 {
        color: #00ff88;
        text-shadow: 0 0 10px rgba(0, 255, 136, 0.5);
        border-bottom: 2px solid #00ff88;
        padding-bottom: 10px;
    }
    
    .stMarkdown h4 {
        color: #64ffda;
        margin-top: 25px;
    }
    
    .stMarkdown code {
        background: rgba(0, 255, 136, 0.1);
        color: #00ff88;
        padding: 2px 6px;
        border-radius: 5px;
    }
    
    .stMarkdown pre {
        background: rgba(0, 20, 40, 0.9);
        border: 1px solid #00ff88;
        border-radius: 10px;
        padding: 15px;
    }
    
    /* Spinner */
    .stSpinner {
        color: #00ff88;
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
api_key = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-pro')

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
    # ...existing code...
st.title("🤖 Futuristic AI Content Rewriter")
st.markdown("""
    <div style='font-size:20px; color:#00fff7;'>
        Generate and rewrite content with advanced AI and human-like style.<br>
        <span style='color:#e0e0e0;'>Powered by Gemini Pro & NLP magic.</span>
    </div>
    """, unsafe_allow_html=True)

prompt = st.text_input("Enter your prompt:", "How does AI impact education?")
intensity = st.slider("Rewrite Intensity (Synonym Replacement Rate)", 0.0, 1.0, 0.3, 0.05)

# --- Clean Markdown Formatting ---
def structure_markdown(prompt, text, intensity_value):
    # Clean up any excessive spacing and normalize text
    text = ' '.join(text.split())
    
    # Split text into paragraphs based on natural breaks
    paragraphs = []
    current_paragraph = ""
    
    sentences = text.split('. ')
    for sentence in sentences:
        sentence = sentence.strip()
        if sentence:
            current_paragraph += sentence + ". "
            # Create paragraph break after 3-4 sentences or if sentence indicates new topic
            if (len(current_paragraph.split('. ')) >= 4 or 
                any(indicator in sentence.lower() for indicator in ['however', 'furthermore', 'moreover', 'in conclusion', 'additionally'])):
                paragraphs.append(current_paragraph.strip())
                current_paragraph = ""
    
    if current_paragraph.strip():
        paragraphs.append(current_paragraph.strip())
    
    md = "### 📝 Original Prompt\n"
    md += f"```text\n{prompt}\n```\n\n"
    md += "---\n\n"
    md += "### ✨ Rewritten Content\n\n"
    
    for paragraph in paragraphs:
        if paragraph:
            # Check if it looks like a heading (short, no ending period, title case)
            if (len(paragraph) < 80 and 
                not paragraph.endswith('.') and 
                paragraph.count(' ') < 8):
                md += f"#### {paragraph}\n\n"
            else:
                md += f"{paragraph}\n\n"
    
    md += "---\n\n"
    md += "### 🎯 Summary\n\n"
    md += "- **Generated by:** Gemini 2.5 Pro AI Model\n"
    md += "- **Enhanced with:** Intelligent synonym replacement, rule-based paraphrasing, and minimal noise injection\n"
    md += f"- **Rewrite Intensity:** {int(intensity_value * 100)}%\n"
    md += "- **Purpose:** Create unique, readable content while preserving original meaning and structure\n"
    
    return md

if st.button("Generate & Rewrite"):
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
        with st.spinner("Rewriting content with AI pipeline..."):
            # Step 1: AI Synonym Replacement
            st.text("Step 1/3: AI Synonym Replacement...")
            rewritten = ai_synonym_replacement(ai_text, intensity)
            
            # Step 2: AI Paraphrasing
            st.text("Step 2/3: AI Paraphrasing...")
            rewritten = ai_paraphrasing(rewritten)
            
            # Step 3: AI Humanization
            st.text("Step 3/3: AI Humanization...")
            rewritten = ai_humanization(rewritten)
        structured_output = structure_markdown(prompt, rewritten, intensity)
        st.markdown(structured_output, unsafe_allow_html=False)
        st.download_button(
            label="Download as .txt",
            data=rewritten,
            file_name="rewritten_content.txt",
            mime="text/plain"
        )
    else:
        st.warning("No content generated. Please try again.")

st.markdown("""
    <hr style='border:1px solid #00fff7;'>
    <div style='text-align:center; color:#00fff7;'>
        <b>Made for Streamlit Cloud • {}</b>
    </div>
    """.format(os.getenv('USER', '2025')), unsafe_allow_html=True)
