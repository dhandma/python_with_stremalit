Project Overview: PDF Chatbot Assistant
This Streamlit application allows users to upload a PDF, which is then embedded using OpenAI embeddings and stored in Qdrant. The user can ask questions about the PDF, and the app will retrieve relevant content from the document and generate contextual answers using OpenAI's GPT model.

🧩 Key Components and Explanation
✅ 1. Environment Setup
python
Copy
Edit
from dotenv import load_dotenv
load_dotenv()
Loads environment variables (like your OpenAI API key) from a .env file.

🤖 2. Import Required Libraries
langchain_qdrant: For vector storage and retrieval

langchain_openai: For OpenAI embeddings

PyPDFLoader: For loading PDFs into text chunks

RecursiveCharacterTextSplitter: For splitting large documents into manageable chunks

openai: For generating responses via GPT-4.1

streamlit: For the UI

tempfile, os, time: For handling uploads and temporary storage

📄 3. Streamlit Page and Styling
python
Copy
Edit
st.set_page_config(...)
Sets up the Streamlit page layout.

html
Copy
Edit
<style>
  .block-container { padding-top: 70px !important; }
  ...
</style>
Adds padding below the Streamlit deploy header and defines message bubble styles.

📤 4. File Upload and Embedding
python
Copy
Edit
uploaded_file = st.file_uploader(...)
Allows the user to upload a PDF file.

python
Copy
Edit
loader = PyPDFLoader(...)
splitter = RecursiveCharacterTextSplitter(...)
splitted_docs = splitter.split_documents(docs)
Loads and splits the PDF into chunks for embedding.

python
Copy
Edit
QdrantVectorStore.from_documents(...)
Embeds and stores these chunks in a local Qdrant collection called "vector_learning".

📦 5. Vector DB Initialization
python
Copy
Edit
vector_db = QdrantVectorStore.from_existing_collection(...)
Tries to connect to an existing Qdrant collection for retrieval.

If none is found, the user is prompted to upload a PDF.

💬 6. Chat State Management
python
Copy
Edit
if "messages" not in st.session_state:
    st.session_state.messages = []
Maintains a persistent chat history using Streamlit’s session state.

💡 7. User Interaction and Rerun Logic
python
Copy
Edit
user_query = st.chat_input(...)
Captures user input from the chat bar.

python
Copy
Edit
if user_query:
    st.session_state.messages.append(...)
    st.rerun()
Appends the user query and a temporary "thinking..." message, then reruns the app.

🔍 8. Query Processing and Response Generation
python
Copy
Edit
search_results = vector_db.similarity_search(...)
Performs a vector similarity search on the query.

python
Copy
Edit
SYSTEM_PROMPT = f"...{context}..."
response = client.chat.completions.create(...)
Builds a system prompt with relevant context and queries OpenAI GPT for a response.

💬 9. Displaying Chat Messages
python
Copy
Edit
for msg in st.session_state.messages:
    ...
Iterates over the chat history and renders messages with proper alignment and styles using embedded HTML and CSS.

✅ Features Summary
Feature	Description
📤 PDF Upload	Upload and process a PDF document
🧠 Vector Embedding	Split and embed PDF using OpenAI Embeddings and Qdrant
🔎 Similarity Search	Retrieve relevant chunks using vector similarity
💬 Chat Interface	Ask natural language questions and get contextual answers
🧾 Page-aware Responses	Assistant refers to PDF content and page numbers in answers
🎨 Custom Styling	Chat bubbles with distinct user and bot styling

🚀 Run the App Locally
bash
Copy
Edit
pip install -r requirements.txt
streamlit run app.py
Make sure Qdrant is running locally at http://localhost:6333 and .env contains your OpenAI API key.

🛠️ .env File
env
Copy
Edit
OPENAI_API_KEY=your_openai_key_here
