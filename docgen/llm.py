import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional

from pydantic_models import DocString, Prompt


load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def llm_docstring_args(code) -> ChatCompletion:
    """Generate a docstring for a given function"""
    
    # the model is forced to return the function docstring.
    return client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a google style docstring generator. You will be given a function and a list of functions that it uses. Generate a docstring for only the main function."
                },
                {
                    "role": "user",
                    "content": code
                },
            ],
            tools=[
                {
                    "type": "function",
                    "function": {
                        "name": "Docstring",
                        "description": "A docstring for an arbitrary function. Include the name of the function.",
                        "parameters": DocString.model_json_schema()
                    },
                    },
                ],
            # enforce the model to only use the function rather than arbitrarily generating what it wants.
            tool_choice={
                "type": "function",
                "function": {"name": "Docstring"}
            }
    )

def generate_docstring(code: str, functions_used: list[tuple[str, str]]) -> DocString:
    
    prompt = Prompt(code=code, used_functions=functions_used).build_prompt()
    args = llm_docstring_args(prompt).choices[0] \
            .message.tool_calls[0].function.arguments # type: ignore
    try:

        docstring = DocString(**json.loads(args))
        print("Generated docstring for: ", docstring.function_name)
        return docstring

    except Exception as e:
        print("Failed to generate docstring for: ", code)
        print("LLM output:", [args])
        print(e)
        raise e



