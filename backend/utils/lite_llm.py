import sys
import litellm
from backend.compile.utils import my_custom_callback, LiteSkill

# This is the simple sales template.
simple_sale_template = """
- name: system instructions
  role: system
  content: |
    Your are a great sales for BeThere.ai, a startup specialized in building greate conversational 
    service. Draft a short message for the cold call the {{ role }} for {{ company }} and you are 
    meant to be helpful and never harmful to humans.

    {{ company }} is {{ company_description }}   
"""

# This is used only for demoing the data structure to generate the exemplar for reservations.
class Resource:
    # For example: restaurant, dental clinic,
    business_type: str
    # For example, table, hairdresser
    resource_type: str
    # For example, big/small, dye, cut or just trim. This might be separate.
    functionality: str

gen_exemplar_template = """
- name: system instructions
  role: system
  content: |
    Your are a experienced customer support, you understand how user express their intention, explicitly or 
    implicitly. You are tasked to Given the business type: {{business_type}}, resource type: {{resource_type}},  
    service. Draft a short message for the cold call the {{ role }} for {{ company }} and you are 
    meant to be helpful and never harmful to humans.

    {{ company }} is {{ company_description }}   
"""


if __name__ == "__main__":
    litellm.callbacks = [my_custom_callback]
    print(sys.executable)
    
    template_data = {
      "role": "CEO",
      "company": "Hai Di Lao",
      "company_description": "A popular Chinese hotpot restaurant."
    }

    model = LiteSkill("groq/llama-3.1-70b-versatile", simple_sale_template)
    response = model.completion(template_data)

    print(response.choices[0].message.content)