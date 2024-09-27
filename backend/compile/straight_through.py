import jinja2

from jinja2 import Environment, FileSystemLoader

from backend import SchemaFieldMode, SchemaFieldTrueType
from backend.datamodel import (
    Schema,
    PromptStrategyEnum,
    Skill,
    OptimizerEnum,
    Model,
    Agent,
    SignatureCompileRequest,
    SchemaField,
)
from backend.compile.base import (
    load_and_execute_code,
    split_imports,
    split_imports_into_nodes,
)


#
# This base version simply use the input prompt (in prompt poet) directly.
# We will code gen Input/Output, {Schema}Input and {Schema)Output that is pydantic class.
# We will code gen the file, that include all the soft function implementation in the workspace.
# We will code gen a LiteSkill object, {Schema}Impl,
# We will code gen the fastAPI endpoint for this skill.
#


# This generates the base inference code that is served via FastAPI.
class LiteSkillGenerator:
    """This will generate as FastAPI app.py"""

    def __init__(self):
        self.imports = [
            "from prompt_poet import Prompt",
            "import litellm",
            "from fastapi import FastAPI",
            "from pydantic import BaseModel",
        ]

        self.env = Environment(loader=FileSystemLoader("backend/compile/templates"))
        self.codes = []
        self.endpoints = []
        self.template = self.env.get_template("litellm.py.tpl")

    # This is low level api, used to implement the high level api, where we just need to
    # extract the prompt template and
    def generate(
        self, model_label: str, module_label: str, module_prompt: str, schema: Schema
    ):
        model = {"label": model_label}
        agent = {"name": module_label, "prompt": module_prompt}
        return self.template.render(schema=schema, skill=agent, model=model)

    def __call__(self, compile_config: SignatureCompileRequest):
        # Hui, get the information and invoke the low level generate function.
        agent = compile_config.getAgent()

        model_label = "groq/llama-3.1-70b-versatile"
        agent_label = agent.config.get("name")
        agent_prompt = agent.config.get("system_message")
        schema = compile_config.getSchema()

        return self.generate(model_label, agent_label, agent_prompt, schema)


# This provides the commandline
if __name__ == "__main__":
    # We create
    agent = Agent()
    compile_request = SignatureCompileRequest()

    fields = []
    fields.append(
        SchemaField(
            name="role",
            mode=SchemaFieldMode.input,
            type=SchemaFieldTrueType.string,
            description="roel",
            prefix="why",
        )
    )
    fields.append(
        SchemaField(
            name="company",
            mode=SchemaFieldMode.input,
            type=SchemaFieldTrueType.string,
            description="roel",
            prefix="why",
        )
    )
    fields.append(
        SchemaField(
            name="company_description",
            mode=SchemaFieldMode.input,
            type=SchemaFieldTrueType.string,
            description="roel",
            prefix="why",
        )
    )
    fields.append(
        SchemaField(
            name="email",
            mode=SchemaFieldMode.output,
            type=SchemaFieldTrueType.string,
            description="roel",
            prefix="why",
        )
    )

    schema = Schema(name="ColdCall", fields=fields)
    print(schema)

    skill = {
        "name": "ColdCaller",
        "prompt": """
            - name: system instructions
              role: system
              content: |
                Your are a great sales for BeThere.ai, a startup specialized in building greate conversational 
                service. Draft a short message for the cold call the {{ role }} for {{ company }} and you are 
                meant to be helpful and never harmful to humans.
            
                {{ company }} is {{ company_description }}   
            """,
    }
    model_label = "groq/llama-3.1-70b-versatile"
    generator = LiteSkillGenerator()
    code = generator.generate(model_label, skill, schema.model_dump())
    print(code)

    # Hui, this is how you actually call this.
    codes = []  # code are generated as above.
    code = build_source(impls)
