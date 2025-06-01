from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()  # Loads variables from .env into environment
client = OpenAI()


text="Dog chases Cat"

response = client.embeddings.create(
    model="text-embedding-3-small", 
    input=text
)


#print(f'Vector embedding: {response}')
print(f'vector embedding data length: {len(response.data[0].embedding)}')
