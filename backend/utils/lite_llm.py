import sys
import litellm
from prompt_poet import Prompt
from pydantic import BaseModel

raw_template = """
- name: system instructions
  role: system
  content: |
    Your are a great sales for BeThere.ai, a startup specialized in building greate conversational 
    service. Draft a short message for the cold call the {{ role }} for {{ company }} and you are 
    meant to be helpful and never harmful to humans.

    {{ company }} is {{ company_description }}   
"""


class Resource:
    # For example: restaurant, dental clinic,
    business_type: str
    # For example, table, hairdresser
    resource_type: str
    # For example, big/small, dye, cut or just trim. This might be separate.
    functionality: str

def my_custom_callback(kwargs, completion_response, start_time, end_time):
    print(f"Prompt sent to LLM: {kwargs['messages']}")


gen_expression_template = """
- name: system instructions
  role: system
  content: |
    Your are a experienced customer support, you understand how user express their intention, explicitly or 
    implicitly. You are tasked to Given the business type: {{business_type}}, resource type: {{resource_type}},  
    service. Draft a short message for the cold call the {{ role }} for {{ company }} and you are 
    meant to be helpful and never harmful to humans.

    {{ company }} is {{ company_description }}   
"""


template_data = {
  "role": "CEO",
  "company": "Hai Di Lao",
  "company_description": "A popular Chinese hotpot restaurant."
}

prompt = Prompt(
    raw_template=raw_template,
    template_data=template_data
)


class LiteModel:
    def __init__(self, model_name):
        self.model_name = model_name

    def project(self, old_dict):
        new_keys = {"role", "content"}
        return { key : old_dict[key] for key in new_keys}


    def completion(self, prompt):
        response = litellm.completion(
            model=self.model_name,
            messages=list(map(lambda x: self.project(vars(x)), prompt.parts))
        )
        return response

if __name__ == "__main__":
    litellm.callbacks = [my_custom_callback]
    print(sys.executable)
    model = LiteModel("groq/llama-3.1-70b-versatile")
    response = model.completion(prompt)
    print(response.choices[0].message.content)