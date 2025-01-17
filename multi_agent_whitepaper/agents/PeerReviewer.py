# agents/PeerReviewer.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def peer_reviewer(draft: str) -> str:
    """
    Reviews the draft for professional quality, domain accuracy, coherence, and suggests improvements based on professional services content principles
    :param draft: The expanded or enriched text that needs an in-depth professional review
    :return: A peer-reviewed piece of content.
    """

    # 1. Create an Azure client with key
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_PREVIEW_API_VERSION")
    )

    # 2. Read the peer reviewer prompt template
    with open("prompts/PeerReviewerPrompt.txt", "r", encoding="utf-8") as f:
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

    # 5. Extract and return the reviewed content
    peer_reviewed_text = response.choices[0].message.content
    return peer_reviewed_text