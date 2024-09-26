# Copyright OpenCUI 2024.

import ast
import importlib
import sys
from _ast import stmt
from typing import Optional, List, Dict, Callable, Tuple
import litellm
from prompt_poet import Prompt

import astor
from pydantic import BaseModel
from backend import PromptStrategyEnum, Schema, Skill, OptimizerEnum, Model, Collections, Agent, SignatureCompileRequest


class FunctionNameExtractor(ast.NodeVisitor):
    def __init__(self):
        self.function_names = []

    def visit_FunctionDef(self, node):
        self.function_names.append(node.name)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.function_names.append(node.name)
        self.generic_visit(node)


def extract_function_names(source_code):
    tree = ast.parse(source_code)
    extractor = FunctionNameExtractor()
    extractor.visit(tree)
    return extractor.function_names


# Ideally, we should generate the training code and execute it on the fly, as
# there is no reason,
def load_and_execute_code(code, module_name="generated_module"):
    # Create a module specification
    importlib.invalidate_caches()

    spec = importlib.util.spec_from_loader(module_name, loader=None)

    # Create a new module based on the spec
    module = importlib.util.module_from_spec(spec)

    # Add the module to sys.modules
    sys.modules[module_name] = module

    # Execute the code within the module's namespace
    exec(code, module.__dict__)

    return module


def split_imports(source_code):
    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Lists to hold import nodes and other nodes
    import_nodes = []
    other_nodes = []

    # Iterate through the top-level nodes in the AST
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_nodes.append(node)
        else:
            other_nodes.append(node)

    # Create new AST modules for imports and other code
    import_module = ast.Module(body=import_nodes, type_ignores=[])
    other_module = ast.Module(body=other_nodes, type_ignores=[])

    # Convert AST modules back to source code
    import_code = astor.to_source(import_module).strip()
    other_code = astor.to_source(other_module).strip()

    return import_code, other_code


# This is used to create the nodes for later.
def split_imports_into_nodes(source_code):
    # Parse the source code into an AST
    tree = ast.parse(source_code)

    # Lists to hold import nodes and other nodes
    import_nodes = []
    rest_nodes = []

    # Iterate through the top-level nodes in the AST
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            import_nodes.append(node)
        else:
            rest_nodes.append(node)

    # Create new AST modules for imports and other code
    return import_nodes, rest_nodes



# This is the simplistic building where we sequentially go through each build task, each returns a statements,
# We then combine all the imports, and rest together respectively, from these statement, generate a source code
# in str.
def serial_build(
        configs: List[Tuple[SignatureCompileRequest]],
        build: Callable[[SignatureCompileRequest], Tuple[List[stmt], List[stmt]]]) -> str:



    import_nodes = []
    rest_nodes = []

    # We simply go through one config at a time.
    for config in configs:
        stmts = build(config)
        import_nodes.append(stmts.imports)
        rest_nodes.append(stmts.rest)

    # Create new AST modules for imports and other code
    import_module = ast.Module(body=import_nodes, type_ignores=[])
    other_module = ast.Module(body=rest_nodes, type_ignores=[])

    # Convert AST modules back to source code
    import_code = astor.to_source(import_module).strip()
    other_code = astor.to_source(other_module).strip()
    return import_code + "\n" + other_code


# This is used to add more log.
def my_custom_callback(kwargs, completion_response, start_time, end_time):
    print(f"Prompt sent to LLM: {kwargs['messages']}")


# This will be used for all the litellm based skill implementation.
class LiteSkill:
    def __init__(self, model_name, template):
        self.model_name = model_name
        self.template = template

    def project(self, old_dict):
        new_keys = {"role", "content"}
        return { key : old_dict[key] for key in new_keys}

    def completion(self, input_node):
        prompt = Prompt(raw_template=self.template, template_data=input_node)
        response = litellm.completion(
            model=self.model_name,
            messages=list(map(lambda x: self.project(vars(x)), prompt.parts))
        )
        return response


# This should be done from the restful api, so that we can evaluate more things.
def evaluate(
    schema: Schema, strategy: PromptStrategyEnum, implementation: str, evaluate: Agent
):
    # gen.gen_code(schema, strategy, implementation)
    # gen = EvaluationGenerator()
    # gen.gen_evaluate(evaluate)
    # module = gen.load()
    return {"accuracy": 1.0}