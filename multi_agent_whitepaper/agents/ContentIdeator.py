# agents/ContentIdeator.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def content_ideator(feeder_idea: str) -> str:
    """
    Generate a detailed outline from a single-sentence idea using Azure OpenAI.
    :param single_sentence_idea: The core concept to expand into an outline
    :return: A string containing the generated outline in Markdown format
    """

    # 1. Create an Azure client with key
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_PREVIEW_API_VERSION")
    )

    # 2. Read the outline prompt template
    with open("prompts/ContentIdeatorPrompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # 3. Insert the user's single-sentence idea into the prompt
    prompt_text = prompt_template.format(feeder_idea=feeder_idea)

    # 4. Create the chat completion request
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_MODEL"), 
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )

    # 4. Extract and return the outline content
    outline_content = response.choices[0].message.content
    if outline_content == None:
        print("error, None response from content ideator")
    return outline_content
