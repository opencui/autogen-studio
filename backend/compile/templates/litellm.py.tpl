
class {{schema.name}}Request(BaseModel):
    {% for field in schema.fields %}
    {% if field.mode == "input" %} {{field.name}} : {{field.type}} {% endif %}
    {% endfor %}

class {{schema.name}}Response(BaseModel):
    {% for field in schema.fields %}
    {% if field.mode == "output" %} {{field.name}} : {{field.type}} {% endif %}
    {% endfor %}

{{skill.name}}_impl == LiteSkill({{model.model}}, {{skill.prompt}})

@app.post("/{{schema.name}}/")
async def process(item: {{schema.name}}Request):
    return {{schema.name}}_impl.completion(**item)

