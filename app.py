import streamlit as st
import google.generativeai as genai
import os

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="Futuristic AI Content Rewriter",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="auto"
)

# --- Futuristic CSS ---
st.markdown(
    """
    <style>
    body, .stApp {
        background: linear-gradient(135deg, #0f2027, #2c5364);
        color: #e0e0e0;
        font-family: 'Segoe UI', 'Roboto', 'Arial', sans-serif;
    }
    .stTextInput>div>div>input {
        background: #1a2636;
        color: #e0e0e0;
        border-radius: 8px;
    }
    .stSlider>div>div {
        color: #00fff7;
    }
    .stButton>button {
        background: linear-gradient(90deg, #00fff7 0%, #2c5364 100%);
        color: #0f2027;
        border-radius: 8px;
        font-weight: bold;
    }
    .stMarkdown, .stTextArea>div>textarea {
        background: #1a2636;
        color: #e0e0e0;
        border-radius: 8px;
    }
    .stDownloadButton>button {
        background: linear-gradient(90deg, #00fff7 0%, #2c5364 100%);
        color: #0f2027;
        border-radius: 8px;
        font-weight: bold;
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
    Task: Replace {int(intensity * 100)}% of important words in the following text with appropriate synonyms.
    
    Rules:
    - Only replace nouns, verbs, and adjectives
    - Keep the exact same meaning and structure
    - Don't change technical terms or proper nouns
    - Don't change the length significantly
    - Maintain professional tone
    
    Original text: {text}
    
    Return only the text with synonyms replaced, nothing else:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return text

def ai_paraphrasing(text):
    """Step 2: AI paraphrases for better flow"""
    prompt = f"""
    Task: Paraphrase the following text to improve flow and readability.
    
    Rules:
    - Keep the exact same meaning and information
    - Improve sentence structure and transitions
    - Make it sound more natural and fluent
    - Don't add or remove any facts or ideas
    - Maintain the same length approximately
    
    Text to paraphrase: {text}
    
    Return only the paraphrased text, nothing else:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except:
        return text

def ai_humanization(text):
    """Step 3: AI adds natural human-like elements"""
    prompt = f"""
    Task: Make the following text sound more natural and human-like.
    
    Rules:
    - Add appropriate transition words (furthermore, additionally, however, etc.)
    - Vary sentence structure slightly
    - Keep all facts and information unchanged
    - Don't make it sound robotic or repetitive
    - Maintain professional academic tone
    - Only make subtle improvements
    
    Text to humanize: {text}
    
    Return only the humanized text, nothing else:
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
            response = model.generate_content(prompt)
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
