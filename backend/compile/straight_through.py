import jinja2

from jinja2 import Environment, FileSystemLoader

from backend.datamodel import Schema, PromptStrategyEnum, Skill, OptimizerEnum, Model
from backend.compile.base import load_and_execute_code, split_imports, BuildConfig, split_imports_into_nodes
import ast
import astor
import importlib
import sys
import litellm
import pyjson5 as json5
from typing import Tuple, Dict

#
# This base version simply use the input prompt (in prompt poet) directly.
# We will code gen Input/Output, {Schema}Input and {Schema)Output that is pydantic class.
# We will code gen the file, that include all the soft function implementation in the workspace.
# We will code gen a LiteSkill object, {Schema}Impl,
# We will code gen the fastAPI endpoint for this skill.
#

# This generates the base inference code that is served via FastAPI.
class LiteLlmInferenceGenerator:
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

    def __call__(self, build_conf: BuildConfig):
        code = self.template.render(schema=build_conf.schema, skill=build_conf.skill, model=build_conf.model)
        import0, code0 = split_imports_into_nodes(code)
        return


    def gen(self):
        self.codes.append("app = FastAPI()")
        return "\n\n".join(["\n".join(self.imports)] + self.codes + self.endpoints)




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




