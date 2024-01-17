import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional

from docgen.pydantic_models import DocString, Prompt


load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def llm_docstring_args(prompt, prev_response) -> ChatCompletion:
    """Generate a docstring for a given function"""
    messages = [{"role": "system", "content": "You are a google style docstring generator. You will be given a function and a list of functions that it uses. Generate a docstring for only the main function."}]
    # the model is forced to return the function docstring.
    if prev_response[0]:
        messages.extend([
            {"role": "user", "content": prev_response[0]},
            {"role": "assistant", "content": prev_response[1]}
        ])
    messages.append({"role": "user", "content": prompt})
    return client.chat.completions.create(
            model="gpt-4",
            messages=messages, # type: ignore
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

def generate_function_docstring(code: str, functions_used: list[tuple[str, str]], prev_response: Optional[str] = None) -> DocString:
    
    prompt = Prompt(code=code, used_functions=functions_used).build_prompt()
    info_for_llm = (None, None)
    if prev_response:
        info_for_llm = (prev_response, "This response resulted in a JSON decode error. Please try again.")

    logging.info("Making request to LLM")
    args = llm_docstring_args(prompt, info_for_llm).choices[0] \
            .message.tool_calls[0].function.arguments # type: ignore
    try:

        docstring = DocString(**json.loads(args))
        log_message = f"Generated docstring for: {docstring.function_name}"
        logging.info(log_message)
        return docstring

    except json.decoder.JSONDecodeError as e:
        logging.error("Failed to generate docstring for: ", code)
        logging.error("LLM output:", [args])
        logging.error("There was a JSONDecodeError:", e)
        logging.warning("Trying again...")

        return generate_function_docstring(code, functions_used, args)



