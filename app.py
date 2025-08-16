import streamlit as st
import google.generativeai as genai
import nltk
from nltk.corpus import wordnet
import random
import os

# Download NLTK data if not present
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)

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

# --- Paraphrasing Rules ---
PARAPHRASE_RULES = {
    "due to the fact that": "because",
    "in order to": "to",
    "at this point in time": "now",
    "in the event that": "if",
    "with regard to": "about",
    "for the purpose of": "to",
    "in the near future": "soon",
    "a large number of": "many",
    "in spite of the fact that": "although",
    "on account of": "because of"
}

NOISE_PHRASES = [
    "Additionally,",
    "Furthermore,",
    "Moreover,",
    "In particular,",
    "Notably,",
    "Indeed,",
    "Specifically,"
]

# --- Synonym Replacement ---
def synonym_replace(text, intensity):
    words = text.split()
    new_words = []
    for word in words:
        # Only replace if random threshold met, word is alphabetic, and longer than 4 characters
        if random.random() < intensity and word.isalpha() and len(word) > 4:
            syns = wordnet.synsets(word)
            suitable_lemmas = set()
            for syn in syns:
                for l in syn.lemmas():
                    lemma = l.name().replace('_', ' ')
                    # Only use synonyms that are similar length and complexity
                    if (lemma.lower() != word.lower() and 
                        len(lemma) <= len(word) + 3 and 
                        lemma.isalpha()):
                        suitable_lemmas.add(lemma)
            if suitable_lemmas:
                new_word = random.choice(list(suitable_lemmas))
                new_words.append(new_word)
            else:
                new_words.append(word)
        else:
            new_words.append(word)
    return ' '.join(new_words)

# --- Rule-based Paraphrasing ---
def rule_paraphrase(text):
    for phrase, replacement in PARAPHRASE_RULES.items():
        text = text.replace(phrase, replacement)
    return text

# --- Noise Injection ---
def inject_noise(text, rate=0.05):  # Much lower rate
    sentences = text.split('. ')
    new_sentences = []
    for sentence in sentences:
        # Only add noise to some sentences, not every few words
        if random.random() < rate and len(sentence.split()) > 10:
            noise = random.choice(NOISE_PHRASES)
            new_sentences.append(f"{noise} {sentence}")
        else:
            new_sentences.append(sentence)
    return '. '.join(new_sentences)

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
        with st.spinner("Rewriting content..."):
            rewritten = synonym_replace(ai_text, intensity)
            rewritten = rule_paraphrase(rewritten)
            rewritten = inject_noise(rewritten, rate=0.03 + intensity/10)  # Much lower noise rate
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
