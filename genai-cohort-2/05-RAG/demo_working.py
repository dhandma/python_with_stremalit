from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import streamlit as st
import os

# Load environment variables
load_dotenv()

# OpenAI client setup
client = OpenAI()

# Streamlit app settings
st.set_page_config(page_title="PDF Chatbot", layout="wide")
st.title("📄 PDF Chatbot Assistant")

# Custom CSS
st.markdown("""
<style>
body, .stApp {
    background-color: #1e1e1e;
    color: white;
    font-family: 'Segoe UI', sans-serif;
}

.stChatContainer {
    display: flex;
    flex-direction: column;
    justify-content: flex-end;
    gap: 10px;
    padding-bottom: 120px;
}

.user-bubble, .bot-bubble {
    display: flex;
    width: 100%;
}

.user-bubble {
    justify-content: flex-end;
    text-align: right;
}

.bot-bubble {
    justify-content: flex-start;
    text-align: left;
}

.bubble {
    padding: 12px 16px;
    border-radius: 18px;
    max-width: 60%;
    font-weight: 500;
    line-height: 1.4;
    word-wrap: break-word;
}

.user-bubble .bubble {
    background-color: #000;
    color: white;
    border-radius: 18px 18px 0 18px;
}

.bot-bubble .bubble {
    background-color: #1a1a1a;
    color: white;
    border-radius: 18px 18px 18px 0;
}

.fixed-input-container {
    position: fixed;
    bottom: 20px;
    left: 50px;
    right: 50px;
    z-index: 999;
}
</style>
""", unsafe_allow_html=True)

# Embedding model and vector DB
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="vector_learning",
    embedding=embedding_model
)

# Init chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Chat container
chat_container = st.container()
with chat_container:
    st.markdown('<div class="stChatContainer">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
        chat_html = f"""
        <div class="{bubble_class}">
            <div class="bubble">{msg['content']}</div>
        </div>
        """
        st.markdown(chat_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Input box
user_query = st.chat_input("Ask something about the PDF...")

if user_query:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Display user message + spinner
    with chat_container:
        st.markdown('<div class="stChatContainer">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            bubble_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
            chat_html = f"""
            <div class="{bubble_class}">
                <div class="bubble">{msg['content']}</div>
            </div>
            """
            st.markdown(chat_html, unsafe_allow_html=True)

        # Spinner inside bot bubble
        spinner_html = """
        <div class="bot-bubble">
            <div class="bubble"><em>Thinking...</em></div>
        </div>
        """
        spinner_placeholder = st.empty()
        spinner_placeholder.markdown(spinner_html, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Run vector search
    search_results = vector_db.similarity_search(query=user_query)
    context = "\n\n\n".join([
        f"Page Content: {result.page_content}\nPage Number: {result.metadata.get('page_label', 'N/A')}\nFile Location: {result.metadata.get('source', '')}"
        for result in search_results
    ])

    # Construct system prompt
    SYSTEM_PROMPT = f"""
    You are a helpful AI Assistant who answers user queries based on the available context
    retrieved from a PDF file including page contents and page number.

    You should only answer the user based on the following context and navigate the user
    to open the right page number to know more.

    Context:
    {context}
    """

    # Get answer from OpenAI
    response = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_query},
        ]
    )
    reply = response.choices[0].message.content

    # Replace spinner with real answer
    spinner_placeholder.markdown(f"""
    <div class="bot-bubble">
        <div class="bubble">{reply}</div>
    </div>
    """, unsafe_allow_html=True)

    # Save assistant message
    st.session_state.messages.append({"role": "assistant", "content": reply})
