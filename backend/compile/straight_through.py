import jinja2

from jinja2 import Environment, FileSystemLoader

from backend import SchemaFieldMode, SchemaFieldTrueType
from backend.datamodel import Schema, PromptStrategyEnum, Skill, OptimizerEnum, Model, Agent
from backend.compile.base import load_and_execute_code, split_imports, split_imports_into_nodes
import ast
import astor
import importlib
import sys
import litellm
import pyjson5 as json5
from typing import Tuple, Dict

from build.lib.backend import SignatureCompileRequest, SchemaField


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
    def generate(self, model_label: str, prompt_template: str, skill_name: str, schema: Schema):
        skill = {
            "name": skill_name,
            "prompt": prompt_template
        }
        model = {
            "label": model_label
        }
        code = self.template.render(schema=schema, skill=skill, model=model)
        return split_imports_into_nodes(code)

    def __call__(self, compile_config: SignatureCompileRequest):
        # Hui, get the information and invoke the low level generate function.
        pass


    def gen(self):
        self.codes.append("app = FastAPI()")
        return "\n\n".join(["\n".join(self.imports)] + self.codes + self.endpoints)



# We need to have
def compile_and_train(
    strategy: PromptStrategyEnum,
    schema: Schema,
    skill: Skill,
    opt_type: OptimizerEnum,
    opt_config: dict,
    model: Model,
    training_set: list,
    teacher: Model = None,
    label: str = "something_unique",
):

    implementation = {}  # optimizer.compile(module, trainset=training_set)
    implementation["module_type"] = opt_type.value
    implementation["model"] = model.model

    infer_gen = None # LiteInferenceGenerator()
    infer_gen.add_fun(schema, strategy, implementation)
    infer_code = infer_gen.gen()

    return implementation, infer_code



# This provides the commandline
if __name__ == "__main__":
    # We create
    agent = Agent()
    compile_request = SignatureCompileRequest()

    fields = []
    fields.append(SchemaField(name="role", mode=SchemaFieldMode.input, type=SchemaFieldTrueType.string))
    fields.append(SchemaField(name="company", mode=SchemaFieldMode.input, type=SchemaFieldTrueType.string))
    fields.append(SchemaField(name="company_description", mode=SchemaFieldMode.input, type=SchemaFieldTrueType.string))
    fields.append(SchemaField(name="email", mode=SchemaFieldMode.output, type=SchemaFieldTrueType.string))

    schema = Schema(name="ColdCall", fields=fields)
    print(schema)

    skill = {
        "name": "ColdCaller",
        "prompt":
            """
            - name: system instructions
              role: system
              content: |
                Your are a great sales for BeThere.ai, a startup specialized in building greate conversational 
                service. Draft a short message for the cold call the {{ role }} for {{ company }} and you are 
                meant to be helpful and never harmful to humans.
            
                {{ company }} is {{ company_description }}   
            """
    }
    model_label = "groq/llama-3.1-70b-versatile"
    #generator = LiteSkillGenerator()
    #code = generator.generate(model_label, skill, schema.dict())