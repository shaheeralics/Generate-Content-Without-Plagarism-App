import streamlit as st

# Page configuration
st.set_page_config(
    page_title="Futuristic Chat App",
    page_icon="✨",
    layout="wide"
)

# Custom CSS for futuristic design
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(135deg, #1f1c2c, #928dab);
        color: #ffffff;
        font-family: 'Arial', sans-serif;
    }
    .stApp {
        background: transparent;
    }
    .main-container {
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        height: 100vh;
        padding: 2rem;
    }
    .input-container {
        display: flex;
        flex-direction: row;
        align-items: center;
        width: 100%;
        max-width: 600px;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    .input-container textarea {
        flex: 1;
        background: transparent;
        border: none;
        color: #ffffff;
        font-size: 16px;
        resize: none;
        outline: none;
        padding: 0.5rem;
    }
    .send-button {
        background: #6a11cb;
        background: linear-gradient(135deg, #6a11cb, #2575fc);
        border: none;
        border-radius: 8px;
        color: #ffffff;
        padding: 0.5rem 1rem;
        cursor: pointer;
        font-size: 16px;
        margin-left: 1rem;
        transition: background 0.3s;
    }
    .send-button:hover {
        background: linear-gradient(135deg, #2575fc, #6a11cb);
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main container
st.markdown('<div class="main-container">', unsafe_allow_html=True)

# Input area
st.markdown('<div class="input-container">', unsafe_allow_html=True)
user_input = st.text_area("", placeholder="Type your message here...", label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

# Send button
if st.button("Send", key="send_button", help="Send your message"):
    st.write(f"You said: {user_input}")

st.markdown('</div>', unsafe_allow_html=True)
