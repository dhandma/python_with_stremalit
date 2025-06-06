from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from dotenv import load_dotenv
load_dotenv()

from pathlib import Path

pdf_file = Path(__file__).parent / "Hims-and-Hers_Q1-2025-Shareholder-Letter_Final.pdf"
loader = PyPDFLoader(file_path=pdf_file)
docs = loader.load()

#print("Docs", docs[0])

#chunking
text_splitter =RecursiveCharacterTextSplitter(
    chunk_size=1000, 
    chunk_overlap=400
    )

splitted_docs=text_splitter.split_documents(documents=docs)
print("texts", splitted_docs[2]) 

#Vector embedding 
#In this stahe you will require to have an openAI secret key to utilize the openai embedding model. 
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large"
    )
#using embedding model, create embedding of splitter and store in vector databse. 

vector_store = QdrantVectorStore.from_documents(
    documents=splitted_docs,
    url="http://localhost:6333",
    collection_name="vector_learning",
    embedding=embeddings
)
print("Indexing of splited document is completed")


# # # my_rag.py
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_qdrant import QdrantVectorStore
# from dotenv import load_dotenv
# import os

# load_dotenv()

# def index_pdf_to_qdrant(pdf_path):
#     loader = PyPDFLoader(file_path=pdf_path)
#     docs = loader.load()

#     text_splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000, 
#         chunk_overlap=400
#     )
#     splitted_docs = text_splitter.split_documents(documents=docs)

#     embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
#     vector_store = QdrantVectorStore.from_documents(
#         documents=splitted_docs,
#         url="http://localhost:6333",
#         collection_name="vector_learning",
#         embedding=embeddings
#     )

#     return "Indexing of uploaded document is completed"
