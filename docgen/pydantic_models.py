from pydantic import BaseModel, Field
from typing import Optional

class FunctionDocstring(BaseModel):
    function_name: str
    summary: str
    description: str
    parameters: Optional[list[str]] = None
    returns: Optional[str] = None
    raises: Optional[list[str]] = None
    example: Optional[str] = Field(default=None, description="A one line string example of how to use the function")
    yields: Optional[str] = None

class ModuleDocstring(BaseModel):
    summary: str
    additional_info: Optional[str] = Field(default=None, description="Additional information about how to use the module")
    usage: Optional[str] = Field(default=None, description="How the module can be initiated from the command line. Only applicable if the module is a script and has a if __name__ == '__main__' block")

class FunctionPrompt(BaseModel):
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

class ModulePrompt(BaseModel):
    module_name: str
    if_name_main: Optional[str]
    functions: list[tuple[str, str]]

    def build_prompt(self) -> str:
        prompt = f"The following functions are used in this module ({self.module_name}):\n\n"
        for function, docstring in self.functions:
            prompt += f'Function: {function}, Summary: {docstring}\n\n'

        if self.if_name_main:
            prompt += f"The following code is in the if __name__ == '__main__' block:\n\n{self.if_name_main}\n\n"
        else:
            prompt += "This module does not have a if __name__ == '__main__' block.\n\n"
        return prompt
