
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

{{skill.name}}_impl == LiteSkill("{{model.label}}", """{{skill.prompt}}""")

@app.post("/{{skill.name}}/")
async def process(item: {{schema.name}}Request):
    return {{skill.name}}_impl.completion(**item)

