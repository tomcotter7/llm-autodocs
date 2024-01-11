import json
import os

from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI
from openai.types.chat import ChatCompletion
from dotenv import load_dotenv


load_dotenv()
openai_api_key = os.environ["OPENAI_API_KEY"]

client = OpenAI(api_key=openai_api_key)

class Docstring(BaseModel):
    function_name: str
    # We can add regex to validate these, and requery the model with the error if it fails.
    summary: str
    description: str
    # The rest of these are optional - depends on the function!
    parameters: Optional[list[str]]
    returns: Optional[str]
    raises: Optional[list[str]]
    example: Optional[str] = Field(description="A one line string example of how to use the function")
    yields: Optional[str]


def build_docstring(docstring_object: Docstring) -> str:
    """Build the actual docstring from the pydantic model"""

    init_docstring = f'"""{docstring_object.summary}\n\n{docstring_object.description}\n\n'

    def add_string(docstring: str, title: str, content: Optional[str]) -> str:
        if not content:
            return docstring
        docstring += f"{title}:\n\t{content}\n"
        return docstring

    def add_list(docstring: str, title: str, content: Optional[list[str]]) -> str:
        if not content:
            return docstring
        docstring += f"{title}:\n"
        for item in content:
            docstring += f"\t{item}\n"
        return docstring
    
    init_docstring = add_list(init_docstring, "Args", docstring_object.parameters)
    init_docstring = add_string(init_docstring, "Returns", docstring_object.returns)
    init_docstring = add_list(init_docstring, "Raises", docstring_object.raises)
    init_docstring = add_string(init_docstring, "Example", docstring_object.example)
    init_docstring = add_string(init_docstring, "Yields", docstring_object.yields)

    init_docstring += '"""'

    return init_docstring

def generate_docstring(code) -> ChatCompletion:
    """Generate a docstring for a given function"""
    
    # the model is forced to return the function docstring.
    return client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a google style docstring generator"
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
                        "parameters": Docstring.model_json_schema()
                    },
                    },
                ],
            # enforce the model to only use the function rather than arbitrarily generating what it wants.
            tool_choice={
                "type": "function",
                "function": {"name": "Docstring"}
            }
    )

resp = generate_docstring("def add(a: float, b: float) -> float:\n return a + b")

args = resp.choices[0].message.tool_calls[0].function.arguments # type: ignore
print(args)
docstring = Docstring(**json.loads(args))
actual_string = build_docstring(docstring)
print(actual_string)
