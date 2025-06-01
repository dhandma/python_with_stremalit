from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()  # Loads variables from .env into environment
client = OpenAI()
