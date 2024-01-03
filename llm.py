import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def extract_function_name(function_code):
    post_name = function_code.index('(')
    function_name = function_code[:post_name].replace('def ', '').strip()
    return function_name
    
    

def build_user_prompt(function_code, used_functions=[]):
    defintions_of_used_functions = ""
    if used_functions:
        used_functions = [f"{fn}: {doc}" for fn, doc in used_functions]
        defintions_of_used_functions = "You have access to the following functions:\n" + '\n'.join(used_functions)
    prompt = f"{defintions_of_used_functions}\n Produce a google style docstring for this function:\n{function_code}\n\n Only return the docstring, not the function name or code."
    return prompt

def get_docstring(fnccode, used_functions=[]):
    entire_prompt = [
        {
            "role": "system",
            "content": 'You are an assistant that produces Google style python docstrings.\
                You can also comment on the quality of the function based on software craftsmanship principles.\
                Your response should be a JSON object with the following keys:\
                    "docstring" - the docstring produced by the AI\
                    "badly_named" - a boolean indicating whether the function name is badly named\
                    "badly_written" - a boolean indicating whether the function is badly written\
                \n\
                The JSON object should only include newlines in the docstring itself.\
                The docstrings produced should be concise, with a description, and args & returns sections.\
                You may include any other sections you deem necessary.\
                Do not include any "Raises" sections if the function does not explicitly raise any exceptions.\
                If the function makes calls to other functions, you will receive the name and docstring of those functions as well.\
                Do not include the """ at the beginning and end of the docstring.'
        },
        {
            "role": "user",
            "content": build_user_prompt(fnccode, used_functions)
        }
    ]
    
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format={ "type": "json_object" },
        messages=entire_prompt,
        temperature=0.0,
        max_tokens=256,
    )
    output = response.choices[0].message.content
    json_output = json.loads(output)
    
    if json_output['badly_named']:
        print(f"This functions name does not conform to software craftsmanship principles: `{extract_function_name(fnccode)}`. Please think about renaming it to something more descriptive.")
    
    if json_output['badly_written']:
        print(f"This function does not conform to software craftsmanship principles. It should be rewritten:\n\n{fnccode}")
    
    return json_output['docstring']