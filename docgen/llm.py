import json
import logging
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletion
from typing import Optional

from docgen.pydantic_models import FunctionDocstring, FunctionPrompt, ModuleDocstring, ModulePrompt
from docgen.system_prompts import FUNCTION_DOCSTRING_SYSTEM_PROMPT, MODULE_DOCSTRING_SYSTEM_PROMPT


load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def make_call_to_llm(
        system_prompt: str,
        user_prompt: str,
        function_name: str,
        function_desc: str,
        function_params: dict,
        prev_response: tuple[str, str] = ("", "")
) -> ChatCompletion:

    messages = [{"role": "system", "content": system_prompt}]
    if len(prev_response[0]) == 0:
        messages.extend([
            {"role": "user", "content": prev_response[0]},
            {"role": "assistant", "content": prev_response[1]}
        ])
    messages.append({"role": "user", "content": user_prompt})

    return client.chat.completions.create(
            model="gpt-4",
            messages=messages, # type: ignore
            tools=[{
                "type": "function",
                "function": {
                    "name": function_name,
                    "description": function_desc,
                    "parameters": function_params
                }
            }],
            tool_choice={
                "type": "function",
                "function": {"name": function_name}
            }
        )

def generate_function_docstring(code: str, functions_used: list[tuple[str, str]], prev_response: Optional[str] = None) -> FunctionDocstring:
    
    prompt = FunctionPrompt(code=code, used_functions=functions_used).build_prompt()
    info_for_llm = ("", "")
    if prev_response:
        error_message = "This response resulted in a JSON decode error. Please try again."
        info_for_llm = (prev_response, str(error_message))

    logging.info("Making request to LLM for function docstring")
    args = make_call_to_llm(
            FUNCTION_DOCSTRING_SYSTEM_PROMPT,
            prompt,
            "FunctionDocstring",
            "A docstring for an arbitrary function. Include the name of the function.",
            FunctionDocstring.model_json_schema(),
            info_for_llm
    ).choices[0].message.tool_calls[0].function.arguments # type: ignore
    try:

        docstring = FunctionDocstring(**json.loads(args))
        log_message = f"Generated docstring for: {docstring.function_name}"
        logging.info(log_message)
        return docstring

    except json.decoder.JSONDecodeError as e:
        logging.error("Failed to generate docstring for: ", code)
        logging.error("LLM output:", [args])
        logging.error("There was a JSONDecodeError:", e)
        logging.warning("Trying again...")

        return generate_function_docstring(code, functions_used, args)

def generate_module_docstring(
        module_name: str,
        functions: list[tuple[str, str]],
        if_name_main: Optional[str] = None,
        prev_response: Optional[str] = None
) -> ModuleDocstring:

    prompt = ModulePrompt(module_name=module_name, functions=functions, if_name_main=if_name_main).build_prompt()
    info_for_llm = ("", "")
    if prev_response:
        error_message = "This response resulted in a JSON decode error. Please try again."
        info_for_llm = (prev_response, str(error_message))
    log_message = f"Making request to LLM for {module_name} docstring"
    logging.info(log_message)
    args = make_call_to_llm(
            MODULE_DOCSTRING_SYSTEM_PROMPT,
            prompt,
            "ModuleDocstring",
            "A docstring for an arbitrary module.",
            ModuleDocstring.model_json_schema(),
            info_for_llm
    ).choices[0].message.tool_calls[0].function.arguments # type: ignore

    try:
        docstring = ModuleDocstring(**json.loads(args))
        log_message = f"Generated docstring for {module_name}"
        logging.info(log_message)
        return docstring
    except json.decoder.JSONDecodeError as e:
        logging.error("Failed to generate docstring for module: ", module_name)
        logging.error("LLM output:", [args])
        logging.error("There was a JSONDecodeError:", e)
        logging.warning("Trying again...")
        return generate_module_docstring(module_name, functions, args)
