# agents/SearchOptimizer.py

import os
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


def search_optimizer(text: str) -> str:
    """
    Enhances the input document to maximize its visibility on search engines. 
    :param document: The text that needs SEO optimization
    :return: A  document with enhanced discoverability online while maintaining its quality, relevance, and integrity.
    """

    # 1. Create an Azure client with key
    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_KEY"),
        api_version=os.getenv("AZURE_OPENAI_PREVIEW_API_VERSION")
    )

    # 2. Read the SEO optimizer prompt template
    with open("prompts/SearchOptimizerPrompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()


    # 3. Insert the text into the prompt
    prompt_text = prompt_template.format(text=text)


    # 4. Create the chat completion request
    response = client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_MODEL"), 
        messages=[
            {"role": "user", "content": prompt_text}
        ]
    )

    # 5. Extract and return the SEO optimized content
    seo_optimized_content = response.choices[0].message.content
    return seo_optimized_content
