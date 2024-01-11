from pydantic import BaseModel, Field
from typing import Optional

class DocString(BaseModel):
    function_name: str
    summary: str
    description: str
    parameters: Optional[list[str]] = None
    returns: Optional[str] = None
    raises: Optional[list[str]] = None
    example: Optional[str] = Field(default=None, description="A one line string example of how to use the function")
    yields: Optional[str] = None

class Prompt(BaseModel):
    code: str
    used_functions: Optional[list[tuple[str, str]]]

    def build_prompt(self) -> str:
        prompt = f'"""{self.code}\n\n'
        if not self.used_functions:
            return prompt + '"""'

        prompt += "The following functions are used in the above code:\n\n"
        for function, docstring in self.used_functions:
            prompt += f'{function}:\n\t{docstring}\n\n'
        prompt += '"""'
        return prompt
