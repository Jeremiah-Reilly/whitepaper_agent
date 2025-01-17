# agents/ContentExpander.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def content_expander(outline: str) -> str:
    """
    Transform the provided outline into a detailed, coherent, and engaging piece of content.
    :param outline: The content outline
    :return: A stand alone content piece without referencing the outline or mentioning that it was based on an outline.
    """

    # 1. Create an Azure client with key
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_PREVIEW_API_VERSION")
    )

    # 2. Read the content expander prompt template
    with open("prompts/ContentExpanderPrompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # 3. Insert the user's single-sentence idea into the prompt
    prompt_text = prompt_template.format(outline=outline)

    # 4. Create the chat completion request
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_MODEL"), 
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )

    # 4. Extract and return the expanded content
    content = response.choices[0].message.content
    return content
