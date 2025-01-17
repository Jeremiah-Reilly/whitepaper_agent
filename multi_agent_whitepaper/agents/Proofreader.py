# agents/Proofreader.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def proofread(draft: str) -> str:
    """
    Reviews the input document thoroughly for grammar, spelling, punctuation, and style. 
    :param document: The document to proofread
    :return: A final, polished version of the text in markdown code without any additional comments or annotations.
    """

    # 1. Create an Azure client with key
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_PREVIEW_API_VERSION")
    )

    # 2. Read the proofreader prompt template
    with open("prompts/ProofreaderPrompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # 3. Insert the draft into the prompt
    prompt_text = prompt_template.format(draft=draft)

    # 4. Create the chat completion request
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_MODEL"), 
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )

    # 5. Extract and return the proofread content
    proofread_content = response.choices[0].message.content
    return proofread_content
