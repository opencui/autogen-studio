
class {{schema.name}}Request(BaseModel):
    {% for field in schema.fields -%}
    {% if field.mode == "input" %}
    {{field.name}} : {{field.true_type}}
    {% endif %}
    {%- endfor %}

class {{schema.name}}Response(BaseModel):
    {% for field in schema.fields -%}
    {% if field.mode == "output" %}
    {{field.name}} : {{field.true_type}}
    {% endif %}
    {%- endfor %}


class LiteSkill:
    def __init__(self, model_name, template):
        self.model_name = model_name
        self.template = template

    def project(self, old_dict):
        new_keys = {"role", "content"}
        return {key: old_dict[key] for key in new_keys}

    def completion(self, input_node):
        prompt = Prompt(raw_template=self.template, template_data=input_node)
        response = litellm.completion(
            model=self.model_name,
            messages=list(map(lambda x: self.project(vars(x)), prompt.parts)),
        )
        return response

{{skill.name}}_impl = LiteSkill("{{model.label}}", """{{skill.prompt}}""")

@app.post("/{{skill.name}}/")
async def process(item: {{schema.name}}Request):
    return {{skill.name}}_impl.completion(**item)

