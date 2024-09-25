import jinja2

from jinja2 import Environment, FileSystemLoader
from backend.datamodel import Schema, PromptStrategyEnum, Skill, OptimizerEnum, Model
from backend.compile.utils import load_and_execute_code, split_imports
import ast
import astor
import importlib
import sys
import litellm
import pyjson5 as json5
from typing import Tuple, Dict

#
# This base version simply use the input prompt (in prompt poet) directly.
# We will create Input/Output, {Schema}Input and {Schema)Output that is pydantic class.
# We will create the file, that include all the soft function implementation in the workspace.
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
        self.template0 = self.env.get_template("infer.py.tpl")
        self.template1 = self.env.get_template("endpoint.py.tpl")

    def add_fun(
        self, schema: Schema, strategy: PromptStrategyEnum, implementation: str
    ):
        types = self.template0.render(schema=schema)
        import0, code0 = split_imports(types)
        self.imports.append(import0)
        self.codes.append(code0)

        endpoint = self.template1.render(
            schema=schema, strategy=strategy.value, implementation=implementation
        )
        self.endpoints.append(endpoint)

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




