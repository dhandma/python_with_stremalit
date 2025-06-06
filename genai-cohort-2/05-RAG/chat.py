from dotenv import load_dotenv
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from openai import OpenAI
import json
load_dotenv()

client = OpenAI()

# Vector Embeddings
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large"
)

vector_db = QdrantVectorStore.from_existing_collection(
    url="http://localhost:6333",
    collection_name="vector_learning",
    embedding=embedding_model
)

while True:
    # Take User Query
    query = input("> ")

    # Vector similarity search in existing vector DB
    search_results= vector_db.similarity_search(
        query=query
    )

    #print(search_results)

    # Convert results to JSON-serializable format
    formatted_results = []
    for result in search_results:
        formatted_results.append({
            "content": result.page_content,
            "metadata": result.metadata
        })

    # Print results in JSON format
    # print(json.dumps(formatted_results, indent=2))

    context = "\n\n\n".join([f"Page Content: {result.page_content}\nPage Number: {result.metadata['page_label']}\nFile Location: {result.metadata['source']}" for result in search_results])

    SYSTEM_PROMPT = f"""
        You are a helpfull AI Assistant who asnweres user query based on the available context
        retrieved from a PDF file along with page_contents and page number.

        You should only ans the user based on the following context and navigate the user
        to open the right page number to know more.

        Context:
        {context}
    """

    chat_completion = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            { "role": "system", "content": SYSTEM_PROMPT },
            { "role": "user", "content": query },
        ]
    )

    print(f"🤖: {chat_completion.choices[0].message.content}")