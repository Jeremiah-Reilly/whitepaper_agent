# agents/orchestrator_agent.py

import os
from dotenv import load_dotenv
import json
from openai import AzureOpenAI
from .ContentIdeator import content_ideator
from .ContentExpander import content_expander
from .Proofreader import proofread
from .PeerReviewer import peer_reviewer
from .KnowledgeFinder import knowledge_finder
from .SearchOptimizer import search_optimizer
from .Summarizer import summarizer

load_dotenv()  # optional if you're using .env

def orchestrate_feeder_idea(feeder_idea: str) -> str:
    """
    Calls Azure OpenAI with the Orchestrator prompt to produce a plan 
    for how to handle the multi-agent workflow.
    """

    client = AzureOpenAI(
        azure_endpoint = os.getenv("AZURE_OPENAI_4o_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_4o_KEY"),
        api_version=os.getenv("AZURE_OPENAI_4o_API_VERSION")
    )

    tools = [
        {
            "type": "function",
            "function": {
                "name": "content_ideator",
                "description": "Creates an outline from the feeder idea",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "feeder_idea": {
                            "type": "string",
                            "description": "The original feeder idea expressed in a single sentence"
                        }
                    },
                    "required": ["feeder_idea"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "content_expander",
                "description": "Expands an outline into a full draft with paragraphs",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "outline": {
                            "type": "string",
                            "description": "An outline to be expanded"
                        }
                    },
                    "required": ["outline"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "knowledge_finder",
                "description": "Enriches the text with references, data, and citations",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "draft": {
                            "type": "string",
                            "description": "A text draft that needs more data/references"
                        }
                    },
                    "required": ["draft"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "peer_reviewer",
                "description": "Reviews the draft for professional quality, domain accuracy, coherence, and suggests improvements based on professional services content principles",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "draft": {
                            "type": "string",
                            "description": "The enriched text that needs an in-depth professional review"
                        }
                    },
                    "required": ["draft"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "summarizer",
                "description": "Generates a concise summary of the whitepaper or final text, highlighting key points and major conclusions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The content to be summarized"
                        }
                    },
                    "required": ["content"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "search_optimizer",
                "description": "Optimizes text for search engines by integrating keywords, improving headings, and aligning with SEO best practices",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The text that needs SEO optimization"
                        }
                    },
                    "required": ["text"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "proofreader",
                "description": "Proofreads the text for grammar, spelling, punctuation, and style issues",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "draft": {
                            "type": "string",
                            "description": "The text that needs a final proofreading pass"
                        }
                    },
                    "required": ["draft"]
                }
            }
        }
    ]

    try:
        # Load the orchestrator prompt template
        prompt_file = "prompts/OrchestratorPrompt.txt"
        with open(prompt_file, "r", encoding="utf-8") as f:
            prompt_template = f.read()

        # Insert the feeder idea into the prompt
        prompt_text = prompt_template.format(feeder_idea=feeder_idea)

        messages=[
                {"role": "user", "content": prompt_text}
            ]
        
        functions_called = set()
        final_answer = None
        function_calls_made = 0
        last_known_draft = None

        # 3. Loop until the LLM produces a final text answer (i.e., no function call).
        while True:
            response = client.chat.completions.create(
                model=os.getenv("AZURE_OPENAI_4o_MODEL"),
                messages=messages,
                tools=tools,
                tool_choice="auto",
                temperature=float(os.getenv("AZURE_OPENAI_TEMPERATURE"))
            )
            # The last message from the LLM
            message = response.choices[0].message

            if message.tool_calls:
                for tool_call in message.tool_calls:

                    function_calls_made += 1
                    print(function_calls_made)
                    # 3a. The LLM wants to call a function
                    name = tool_call.function.name
                    functions_called.add(name)
                    arguments_str = tool_call.function.arguments  # raw JSON string

                    # Parse arguments
                    try:
                        arguments = json.loads(arguments_str)
                    except json.JSONDecodeError:
                        # If invalid JSON, we can handle error or ignore
                        arguments = {}
                        print(f"Error: invalid json from {name}")

                    # Call the actual python function
                    if name == "content_ideator":
                        print(f"calling {name}")
                        result = content_ideator(**arguments)
                        last_known_draft = result
                    elif name == "content_expander":
                        print(f"calling {name}")
                        result = content_expander(**arguments)
                        last_known_draft = result
                    elif name == "knowledge_finder":
                        print(f"calling {name}")
                        result = knowledge_finder(**arguments)
                        last_known_draft = result
                    elif name == "peer_reviewer":
                        print(f"calling {name}")
                        # Sometimes the model gets stuck not providing the draft to peer reviewer, here we help it along
                        if "draft" not in arguments or not arguments["draft"]:
                            if last_known_draft:
                                arguments["draft"] = last_known_draft
                                result = peer_reviewer(**arguments)
                            else:
                                messages.append({
                                "role": "system",
                                "content": (
                                    "Error: You called peer_reviewer without passing 'draft'. "
                                    "Please provide the 'draft' argument for peer review."
                                )
                                })
                                continue  # Let the LLM try again
                        else:
                            result = peer_reviewer(**arguments)
                        last_known_draft = result
                    elif name == "summarizer":
                        print(f"calling {name}")
                        result = summarizer(**arguments)
                    elif name == "search_optimizer":
                        print(f"calling {name}")
                        result = search_optimizer(**arguments)
                        last_known_draft = result
                    elif name == "proofreader":
                        print(f"calling {name}")
                        # Sometimes the model gets stuck not providing the draft to proofread, here we help it along
                        if "draft" not in arguments or not arguments["draft"]:
                            if last_known_draft:
                                arguments["draft"] = last_known_draft
                                result = proofread(**arguments)
                            else:
                                messages.append({
                                "role": "system",
                                "content": (
                                    "Error: You called proofread without passing 'draft'. "
                                    "Please provide the 'draft' argument for proofread."
                                )
                                })
                                continue  # Let the LLM try again
                        else:
                            result = peer_reviewer(**arguments)
                        last_known_draft = result
                    else:
                        # fallback if the function name is unknown
                        result = f"Error: unknown function '{name}'"

                    # 3b. Provide the function's result back to the LLM as an assistant message
                    #     so it can continue the conversation with updated context.
                    messages.append({
                        "role": "function",
                        "content": result,
                        "name": name  # indicate which agent the result is from
                    })  
            else:
                # (4b) This is a normal text message
                text = message.content
                if text and text.strip():
                    # Possibly the final answer
                    final_answer = text
                    # Check if we have everything we need
                    break
                else:
                    # The model didn't call a function or provide text
                    # Maybe it thinks it's done. But we want a final text
                    messages.append({
                        "role": "user",
                        "content": "All steps appear done. Please give the final whitepaper text now."
                    })
                    continue

            # (5) If we've called all necessary agents, we can *nudge* the model
            # or skip. For example, if all functions have been called (all agents), we can prompt for final text:
            if len(functions_called) >= 7:   # or some condition
                messages.append({
                    "role": "user",
                    "content": "We have completed all tasks. Please now provide the final whitepaper text."
                })
                # We do NOT break. We let the loop continue so the model can respond with normal text.

            # (3c) append the LLM's message to messages if it has text:
            if message.content:
                messages.append({"role": "assistant", "content": message.content})

        return final_answer
    except Exception as e:
        # 6. Dump the entire message log for debugging
        print("ERROR: An exception occurred in orchestrate_feeder_idea.")
        print("Here is the conversation so far:\n")
        for idx, m in enumerate(messages):
            print(f"--- Message {idx} ---")
            print(f"Role: {m.get('role')}")
            print(f"Name: {m.get('name')}")
            print(f"Content: {m.get('content')}")
            print()

        # Optionally, re-raise the exception to see the full traceback
        raise e