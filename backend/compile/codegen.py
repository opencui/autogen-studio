import jinja2
from dspy.teleprompt import BootstrapFewShot
from jinja2 import Environment, FileSystemLoader
from backend.datamodel import Schema, PromptStrategyEnum, Skill, OptimizerEnum, Model
import ast
import astor
import importlib
import sys
import dspy
from typing import Tuple, Dict


# This is used to generate the train and inference code for declared signature.
# The train.py will be used to take accompanied training set, metric, and spits out the model.json file
# The inference.py will take model.json file and serve the llm functionality.
# There are three different code gen tasks:
# 1. training of the single signature/module. We need validation here.
# 2. inference of the single signature/module.
# 3. inference of many signatures/modules.


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


class ImportsGenerator:
    """register the """
    def __init__(self):
        self.imports = []
    def add(self, package):
        self.imports.append(package)

    def __call__(self):
        return self.template.render(packages=self.imports)


class SignatureGenerator:
    def __init__(
            self,
            strategy_value: str,
            template: jinja2.Template,
            opt_type: OptimizerEnum,
            opt_config: Dict,
    ):
        self.strategy = strategy_value
        self.template = template
        self.opt_type = opt_type
        self.opt_config = opt_config

    def __call__(self, schema):
        return self.template.render(
            schema=schema, strategy=self.strategy, opt_type=self.opt_type, opt_config=str(self.opt_config))


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


def generate_module_for_train(
        strategy: PromptStrategyEnum,
        schema: Schema,
        skill: Skill,
        opt_type: str,
        opt_config=None):
    """
    This will generate two files {{schame.name}}_train.py and {{schema.name}}_inference.py under output_path
    Need to make sure the skill.name is the referenced in the training.
    """

    if opt_config is None:
        opt_config = {}
    schema.fields = list(filter(lambda x: x["mode"] != "any", schema.fields))
    num_of_output = len(list(filter(lambda x: x["mode"] == "output", schema.fields)))
    if num_of_output == 0:
        return False, "No output fields"

    # now make sure we have skill for metric:
    function_name = skill.name
    print(function_name)
    functions = extract_function_names(skill.content)
    if function_name not in functions:
        return False, "metric function is not presented"

    # Now we generate both metric function and signature and training
    env = Environment(loader=FileSystemLoader('backend/compile/templates'))
    template = env.get_template("signature.py.tpl")
    generate_signature = SignatureGenerator(strategy.value, template, opt_type, opt_config)

    code = generate_signature(schema)
    print(code)

    imports0, code0 = split_imports(skill.content)
    imports1, code1 = split_imports(code)

    return "\n\n".join([imports0, imports1, code0, code1])


def get_dspy_model(model: Model):
    if model.api_type == "open_ai":
        return dspy.OpenAI(model=model.model, api_key=model.api_key)
    return None


def compile_and_train(
    strategy: PromptStrategyEnum,
    schema: Schema,
    skill: Skill,
    opt_type: OptimizerEnum,
    model: Model,
    training_set: list,
    teacher: Model = None,
    label: str = "something_unique"
):
    code = generate_module_for_train(strategy, schema, skill, opt_type.value, config)
    module = load_and_execute_code(code, module_name=label)
    lm = get_dspy_model(model)
    teacher = get_dspy_model(teacher) if teacher is not None else lm

    dspy.settings.configure(lm=lm)
    teacher_config = {"lm": teacher}
    optimizer = BootstrapFewShot(metric=module.metric, teacher_settings=teacher_config, **module.opt_config)
    implementation = optimizer.compile(module, trainset=training_set)
    implementation["module_type"] = opt_type.value
    return implementation


# This generates the training code.
def generte_fastapi(schemas: list[Schema], output_path):
    """This will generate main.py as FastAPI app.py"""
    None


if __name__ == "__main__":
    schema_dict = {
        "user_id": "guestuser@gmail.com",
        "name": "schema1",
        "description": "desc schema1",
        "fields": [
            {"name": "k1", "description": "desc k1", "true_type": "int", "mode": "input", "prefix": "prefix1,xxxxxx"},
            {"name": "k3", "description": "k3 prefix", "true_type": "any", "mode": "any", "prefix": "prefix3,zzz"},
            {"name": "k2", "description": "k2 prefix", "true_type": "any", "mode": "output", "prefix": "prefix2,yyy"}
        ]}

    metric_dict = {
        "id": 1,
        "created_at": "2024-07-24T07:36:37.289536",
        "updated_at": "2024-07-24T07:36:37.289537",
        "user_id": "guestuser@gmail.com",
        "name": "generate_images",
        "content": "\nfrom typing import List\nimport uuid\nimport requests  # to perform HTTP requests\nfrom pathlib import Path\n\nfrom openai import OpenAI\n\n\ndef generate_images(query: str, image_size: str = \"1024x1024\") -> List[str]:\n    \"\"\"\n    Function to paint, draw or illustrate images based on the users query or request. Generates images from a given query using OpenAI's DALL-E model and saves them to disk.  Use the code below anytime there is a request to create an image.\n\n    :param query: A natural language description of the image to be generated.\n    :param image_size: The size of the image to be generated. (default is \"1024x1024\")\n    :return: A list of filenames for the saved images.\n    \"\"\"\n\n    client = OpenAI()  # Initialize the OpenAI client\n    response = client.images.generate(model=\"dall-e-3\", prompt=query, n=1, size=image_size)  # Generate images\n\n    # List to store the file names of saved images\n    saved_files = []\n\n    # Check if the response is successful\n    if response.data:\n        for image_data in response.data:\n            # Generate a random UUID as the file name\n            file_name = str(uuid.uuid4()) + \".png\"  # Assuming the image is a PNG\n            file_path = Path(file_name)\n\n            img_url = image_data.url\n            img_response = requests.get(img_url)\n            if img_response.status_code == 200:\n                # Write the binary content to a file\n                with open(file_path, \"wb\") as img_file:\n                    img_file.write(img_response.content)\n                    print(f\"Image saved to {file_path}\")\n                    saved_files.append(str(file_path))\n            else:\n                print(f\"Failed to download the image from {img_url}\")\n    else:\n        print(\"No image data found in the response!\")\n\n    # Return the list of saved files\n    return saved_files\n\n\n# Example usage of the function:\n# generate_and_save_images(\"A cute baby sea otter\")\n",
        "description": "Generate and save images based on a user's query.",
        "secrets": {},
        "libraries": {}
        }

    schema = Schema(**schema_dict)
    skill = Skill(**metric_dict)

    strategy = PromptStrategyEnum.chain_of_thought
    optimizer = OptimizerEnum.bootstrap_few_shot
    print(optimizer.value)
    config = {}
    print(str(config))
    code = generate_module_for_train(strategy, schema, skill, optimizer.value, config)

    print(code)

    module = load_and_execute_code(code, module_name="something_unique")

