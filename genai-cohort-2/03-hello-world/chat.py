from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()  # Loads variables from .env into environment
client = OpenAI()

response=client.chat.completions.create(
    model="gpt",
    messages=[
        {"role":"user", "content":"Hey, My name is Mayur Dhande"},
    ]
)

print(response.choices[0].message.content)