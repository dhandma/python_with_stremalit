# from cot_prompt import SYSTEM_PROMPT  # You must define this in your code
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import json
import os

# Load environment variables
load_dotenv()
client = OpenAI()

st.set_page_config(page_title="ChatGPT-like UI", layout="wide")
st.title("🧠 MY FIRST CHATMODEL")

# Custom CSS for full chat experience
st.markdown("""
<style>
body, .stApp {
    background-color: #F0F2F6 !important;
    color: black;
}

/* Center the chat area */
.stChatContainer {
    display: flex;
    justify-content: center;
}

/* Chat bubble containers */
.user-bubble, .bot-bubble {
    display: flex;
    margin: 10px 0;
}

.user-bubble {
    justify-content: flex-start;
}

.bot-bubble {
    justify-content: flex-end;
}

/* Chat bubbles */
.bubble {
    padding: 12px 16px;
    border-radius: 18px;
    max-width: 60%;
    font-weight: 500;
    line-height: 1.4;
}

.user-bubble .bubble {
    background-color: #00C851;
    color: white;
    border-radius: 18px 18px 18px 0;
}

.bot-bubble .bubble {
    background-color: #DDDDDD;
    color: black;
    border-radius: 18px 18px 0 18px;
}

/* Fancy dot loader */
.dot-loader {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 30px;
    margin: 10px 0;
}

.dot-loader span {
    display: inline-block;
    width: 10px;
    height: 10px;
    margin: 0 4px;
    background-color: #888;
    border-radius: 50%;
    animation: bounce 1.4s infinite ease-in-out both;
}

.dot-loader span:nth-child(1) {
    animation-delay: -0.32s;
}
.dot-loader span:nth-child(2) {
    animation-delay: -0.16s;
}
.dot-loader span:nth-child(3) {
    animation-delay: 0s;
}

@keyframes bounce {
    0%, 80%, 100% { transform: scale(0); }
    40% { transform: scale(1); }
}
</style>
""", unsafe_allow_html=True)

# Initialize session
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# Display messages
st.markdown('<div class="stChatContainer">', unsafe_allow_html=True)
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages[1:]:  # Skip system prompt
        is_user = msg["role"] == "user"
        bubble_class = "user-bubble" if is_user else "bot-bubble"
        chat_html = f"""
        <div class="{bubble_class}">
            <div class="bubble">{msg['content']}</div>
        </div>
        """
        st.markdown(chat_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Input from user
user_query = st.chat_input("Enter your problem or question...")

if user_query:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Display user bubble
    with chat_container:
        st.markdown(f"""
        <div class="user-bubble">
            <div class="bubble">{user_query}</div>
        </div>
        """, unsafe_allow_html=True)

    # Show loading animation
    thinking_placeholder = st.empty()
    with thinking_placeholder.container():
        st.markdown("""
        <div class="bot-bubble">
            <div class="bubble">
                <div class="dot-loader">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Generate bot response
    step_outputs = []
    while True:
        response = client.chat.completions.create(
            model="gpt-4.1",
            response_format={"type": "json_object"},
            messages=st.session_state.messages,
        )
        assistant_message = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": assistant_message})

        try:
            parsed = json.loads(assistant_message)
            step = parsed.get("step", "")
            content = parsed.get("content", "")
        except json.JSONDecodeError:
            step = "result"
            content = assistant_message  # fallback

        step_outputs.append((step, content))
        if step == "result":
            break

    # Replace loader with actual response
    thinking_placeholder.empty()

    for step, content in step_outputs:
        if step == "result":
            st.markdown(f"""
            <div class="bot-bubble">
                <div class="bubble">{content}</div>
            </div>
            """, unsafe_allow_html=True)
