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
    def generate(self, model_label: str, prompt_template: str, schema: Schema):
        code = self.template.render(schema=agent.schema, skill=agent, model=agent.models[0])
        import0, code0 = split_imports_into_nodes(code)

    def __call__(self, agent: Agent, compile_config: SignatureCompileRequest):
        code = self.template.render(schema=agent.schema, skill=agent, model=agent.models[0])
        import0, code0 = split_imports_into_nodes(code)
        return


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