# agents/KnowledgeFinder.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def knowledge_finder(draft: str) -> str:
    """
    Enriches the text with references, data, and citations
    :param draft: A text draft that needs more data/references
    :return: A data and reference enriched piece of content.
    """

    # 1. Create an Azure client with key
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_PREVIEW_API_VERSION")
    )

    # 2. Read the knowledge finder prompt template
    with open("prompts/KnowledgeFinderPrompt.txt", "r", encoding="utf-8") as f:
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

    # 5. Extract and return the revised content
    enriched_text = response.choices[0].message.content
    # print(enriched_text)
    return enriched_text