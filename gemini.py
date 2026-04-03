import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

system_prompt = """
You are a helpful AI assistant for this application.
You ONLY answer questions related to this app's purpose.
If asked anything unrelated respond with:
"I can only assist with queries related to this application."
"""

def generate_response(prompt: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
# from groq import Groq
# from dotenv import load_dotenv
# import os

# load_dotenv()

# # Create Groq client with your API key
# client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# # System prompt — controls what AI does and doesn't do
# system_prompt = """
# You are a helpful AI assistant for this application.
# You ONLY answer questions related to this app's purpose.
# If asked anything unrelated respond with:
# "I can only assist with queries related to this application."
# """

# def generate_response(prompt: str) -> str:
#     # Send message to Groq
#     response = client.chat.completions.create(
#         model="llama-3.3-70b-versatile",  # best free model on Groq
#         messages=[
#             {"role": "system", "content": system_prompt},  # sets AI behavior
#             {"role": "user", "content": prompt}  # user's message
#         ]
#     )
#     # Extract and return the text response
#     return response.choices[0].message.content