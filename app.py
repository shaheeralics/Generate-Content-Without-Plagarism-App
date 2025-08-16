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
def inject_noise(text, rate=0.15):
    words = text.split()
    n = max(1, int(len(words) * rate))
    positions = random.sample(range(len(words)), n)
    for pos in sorted(positions, reverse=True):
        noise = random.choice(NOISE_PHRASES)
        words.insert(pos, noise)
    return ' '.join(words)

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
    # Split text into paragraphs
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    md = "### 📝 Original Prompt\n"
    md += f"```text\n{prompt}\n```\n\n"
    md += "---\n\n"
    md += "### ✨ Rewritten Content\n\n"
    
    for i, paragraph in enumerate(paragraphs, 1):
        # Check if paragraph looks like a heading (short and no period at end)
        if len(paragraph) < 100 and not paragraph.endswith('.'):
            md += f"#### {paragraph}\n\n"
        else:
            # Split long paragraphs into sentences for better readability
            sentences = [s.strip() for s in paragraph.split('. ') if s.strip()]
            if len(sentences) > 1:
                # Multiple sentences - format as paragraph
                formatted_paragraph = '. '.join(sentences)
                if not formatted_paragraph.endswith('.'):
                    formatted_paragraph += '.'
                md += f"{formatted_paragraph}\n\n"
            else:
                # Single sentence - format as is
                md += f"{paragraph}\n\n"
    
    md += "---\n\n"
    md += "### 🎯 Summary\n\n"
    md += "- **Generated by:** Gemini 2.5 Pro AI Model\n"
    md += "- **Enhanced with:** Synonym replacement, rule-based paraphrasing, and human-like noise injection\n"
    md += f"- **Rewrite Intensity:** {int(intensity_value * 100)}%\n"
    md += "- **Purpose:** Create unique, human-like content while preserving original meaning\n"
    
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
            rewritten = inject_noise(rewritten, rate=0.12 + intensity/2)
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
