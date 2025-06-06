from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from openai import OpenAI
import streamlit as st
import os
import tempfile
from pathlib import Path
import time

# Load environment variables
load_dotenv()

# Set up OpenAI client
client = OpenAI()

# Page config
st.set_page_config(page_title="PDF Chatbot", layout="wide")

# Sticky Header and File Upload CSS Fixes
st.markdown("""
    <style>
    /* Padding below top pane */
    .block-container {
        padding-top: 70px !important;
    }

    .user-message {
        text-align: right;
        background-color: #DCF8C6;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 15px;
        display: inline-block;
        max-width: 75%;
        float: right;
        clear: both;
    }

    .bot-message {
        text-align: left;
        background-color: #F1F0F0;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 15px;
        display: inline-block;
        max-width: 75%;
        float: left;
        clear: both;
    }
    </style>
""", unsafe_allow_html=True)



# Header HTML
st.markdown("""
<div id="fixed-header">
    <h2 style="margin: 0; color: white;">📄 PDF Chatbot Assistant</h2>
</div>
""", unsafe_allow_html=True)

# File upload at top-right corner
st.markdown('<div class="file-upload-container">', unsafe_allow_html=True)
uploaded_file = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed", key="top_pdf")
if uploaded_file:
    st.session_state.uploaded_filename = uploaded_file.name

    # Save to temp and process embedding
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        tmp_file_path = tmp_file.name

    loader = PyPDFLoader(file_path=tmp_file_path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=400)
    splitted_docs = splitter.split_documents(docs)
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

    QdrantVectorStore.from_documents(
        documents=splitted_docs,
        url="http://localhost:6333",
        collection_name="vector_learning",
        embedding=embedding_model
    )

    temp_msg = st.empty()
    temp_msg.success(f"Uploaded: {uploaded_file.name}\nVector embedding completed!")
    time.sleep(2)
    temp_msg.empty()

st.markdown('</div>', unsafe_allow_html=True)

# Initialize vector_db if available
embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")
vector_db = None
try:
    vector_db = QdrantVectorStore.from_existing_collection(
        url="http://localhost:6333",
        collection_name="vector_learning",
        embedding=embedding_model
    )
except Exception:
    st.warning("No vector DB found yet. Please upload a PDF to initialize search.")

# Chat history state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Input bar
user_query = st.chat_input("Ask something about the PDF...")

# If user submits a query
if user_query:
    st.session_state.messages.append({"role": "user", "content": user_query})
    st.session_state.messages.append({"role": "assistant", "content": "⏳ Thinking..."})
    st.rerun()

# Process assistant message
if st.session_state.messages and st.session_state.messages[-1]["content"] == "⏳ Thinking...":
    user_query = next((m["content"] for m in reversed(st.session_state.messages) if m["role"] == "user"), "")
    if vector_db:
        search_results = vector_db.similarity_search(query=user_query)
        context = "\n\n\n".join([
            f"Page Content: {doc.page_content}\nPage Number: {doc.metadata.get('page_label', 'N/A')}\nFile Location: {doc.metadata.get('source', '')}"
            for doc in search_results
        ])

        SYSTEM_PROMPT = f"""
        You are a helpful AI Assistant who answers user queries based on the available context
        retrieved from a PDF file including page contents and page number.

        You should only answer the user based on the following context and navigate the user
        to open the right page number to know more.

        Context:
        {context}
        """

        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_query},
            ]
        )
        final_reply = response.choices[0].message.content
        st.session_state.messages[-1] = {"role": "assistant", "content": final_reply}
        st.rerun()

# Chat display
st.markdown('<div class="stChatContainer">', unsafe_allow_html=True)
chat_container = st.container()
with chat_container:
    for msg in st.session_state.messages:
        is_user = msg["role"] == "user"
        bubble_class = "user-bubble" if is_user else "bot-bubble"
        chat_html = f"""
        <div class="{bubble_class}">
            <div class="bubble">{msg['content']}</div>
        </div>
        """
        st.markdown(chat_html, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
