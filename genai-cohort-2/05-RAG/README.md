📄 PDF Chatbot Assistant
This project allows you to upload a PDF file and chat with it using OpenAI's GPT-4.1 model. The PDF content is embedded into a Qdrant vector database and queried intelligently to answer your questions.

🔧 Features
Upload PDF files via the UI (max 200MB)

Content is chunked and indexed using LangChain + Qdrant

Ask questions related to the uploaded PDF

Answers are based on vector similarity context from the document

Clean, dark-themed chat interface

🚀 How to Run
1. Install Dependencies
   ```
   pip install -r requirements.txt
    streamlit
    langchain
    qdrant-client
    langchain-openai
    openai
    python-dotenv
   ```

2. Start Qdrant
Make sure Qdrant is running locally on port 6333. You can use Docker:
```
      docker run -p 6333:6333 -p 6334:6334 qdrant/qdrant
```

3. Set OpenAI Key
In demo.py, replace this line with your actual key:

```
os.environ["OPENAI_API_KEY"] = "your-openai-api-key"
```
Or set it in your shell:

```
export OPENAI_API_KEY=your-openai-api-key
```

4. Run the App using streamlit
```
streamlit run demo.py
```
💬 Usage
Upload any PDF using the drag-and-drop uploader in the top-right corner.

Ask a question in the input bar.

See the assistant respond using retrieved content from the PDF.

📦 Folder Structure that is helpful 
```
      .
      ├── demo.py            # Main Streamlit app
      ├── requirements.txt   # Python dependencies
      |__ chat.py
      |__ my_rag.py
      └── README.md          # You're here!

```

🧠 Tech Stack
Streamlit: UI and interactivity

LangChain: Document parsing, splitting, embedding

Qdrant: Vector storage and similarity search

OpenAI GPT-4.1: Response generation

