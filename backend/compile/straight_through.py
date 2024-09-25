import jinja2

from jinja2 import Environment, FileSystemLoader
from backend.datamodel import Schema, PromptStrategyEnum, Skill, OptimizerEnum, Model
from backend.compile.utils import load_and_execute_code
import ast
import astor
import importlib
import sys
import litellm
import pyjson5 as json5
from typing import Tuple, Dict


# This is used to generate the train and inference code for declared signature.
# The train.py will be used to take accompanied training set, metric, and spits out the model.json file
# The inference.py will take model.json file and serve the llm functionality.
# There are three different code gen tasks:
# 2. evaluate the single signature/module.
# 3. inference of the single signature/module for adhoc testing.
# 4. inference of many signatures/modules for export.

# This base version simply use the input prompt (in prompt poet) directly.
# We will create Input/Output, {Schema}Input and {Schema)Output that is pydantic class.
# We will create the file, that include all the soft function implementation in the workspace.


class LiteSkill:
    def __init__(self, model: Model, skill: Skill, schema: Schema):
        self.model_name = model

    def project(self, old_dict):
        new_keys = {"role", "content"}
        return { key : old_dict[key] for key in new_keys}


    def completion(self, prompt):
        response = litellm.completion(
            model=self.model_name,
            messages=list(map(lambda x: self.project(vars(x)), prompt.parts))
        )
        return response


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

    infer_gen = InferenceGenerator()
    infer_gen.add_fun(schema, strategy, implementation)
    infer_code = infer_gen.gen()

    return implementation, infer_code


class EvaluationGenerator:
    def __init__(self):
        self.imports = ["import dspy"]

        self.env = Environment(loader=FileSystemLoader("backend/compile/templates"))
        self.codes = []
        self.template0 = self.env.get_template("evaluate.py.tpl")

    def gen_code(
        self,
        schema: Schema,
        strategy: PromptStrategyEnum,
        implementation: str,
        skill: Skill,
    ):
        self.codes.append(
            self.template1.render(
                schema=schema,
                strategy=strategy.value,
                implementation=implementation,
                skill=skill,
            )
        )

    def gen_evaluate(self, eval: Skill):
        imports0, codes0 = split_imports(eval.content)
        self.imports.append(imports0)
        self.codes.append(codes0)

    # the module.eval, module.module can be used directly for evaluation.
    def load(self, module_name="random"):
        code = "\n\n".join(["\n".join(self.imports)] + self.codes)
        module = load_and_execute_code(code, module_name)
        return module


def evaluate(
    schema: Schema, strategy: PromptStrategyEnum, implementation: str, evaluate: Skill
):
    # gen.gen_code(schema, strategy, implementation)
    # gen = EvaluationGenerator()
    # gen.gen_evaluate(evaluate)
    # module = gen.load()
    return {"accuracy": 1.0}


# This generates the inference code that is served via FastAPI.
class InferenceGenerator:
    """This will generate main.py as FastAPI app.py"""

    def __init__(self):
        self.imports = [
            "import dspy",
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





if __name__ == "__main__":
    schema_dict = {
        "user_id": "guestuser@gmail.com",
        "name": "schema1",
        "description": "desc schema1",
        "fields": [
            {
                "name": "k1",
                "description": "desc k1",
                "true_type": "int",
                "mode": "input",
                "prefix": "prefix1,xxxxxx",
            },
            {
                "name": "k3",
                "description": "k3 prefix",
                "true_type": "str",
                "mode": "any",
                "prefix": "prefix3,zzz",
            },
            {
                "name": "k2",
                "description": "k2 prefix",
                "true_type": "str",
                "mode": "output",
                "prefix": "prefix2,yyy",
            },
        ],
    }

    metric_dict = {
        "id": 1,
        "created_at": "2024-07-24T07:36:37.289536",
        "updated_at": "2024-07-24T07:36:37.289537",
        "user_id": "guestuser@gmail.com",
        "name": "generate_images",
        "content": '\nfrom typing import List\nimport uuid\nimport requests  # to perform HTTP requests\nfrom pathlib import Path\n\nfrom openai import OpenAI\n\n\ndef generate_images(query: str, image_size: str = "1024x1024") -> List[str]:\n    """\n    Function to paint, draw or illustrate images based on the users query or request. Generates images from a given query using OpenAI\'s DALL-E model and saves them to disk.  Use the code below anytime there is a request to create an image.\n\n    :param query: A natural language description of the image to be generated.\n    :param image_size: The size of the image to be generated. (default is "1024x1024")\n    :return: A list of filenames for the saved images.\n    """\n\n    client = OpenAI()  # Initialize the OpenAI client\n    response = client.images.generate(model="dall-e-3", prompt=query, n=1, size=image_size)  # Generate images\n\n    # List to store the file names of saved images\n    saved_files = []\n\n    # Check if the response is successful\n    if response.data:\n        for image_data in response.data:\n            # Generate a random UUID as the file name\n            file_name = str(uuid.uuid4()) + ".png"  # Assuming the image is a PNG\n            file_path = Path(file_name)\n\n            img_url = image_data.url\n            img_response = requests.get(img_url)\n            if img_response.status_code == 200:\n                # Write the binary content to a file\n                with open(file_path, "wb") as img_file:\n                    img_file.write(img_response.content)\n                    print(f"Image saved to {file_path}")\n                    saved_files.append(str(file_path))\n            else:\n                print(f"Failed to download the image from {img_url}")\n    else:\n        print("No image data found in the response!")\n\n    # Return the list of saved files\n    return saved_files\n\n\n# Example usage of the function:\n# generate_and_save_images("A cute baby sea otter")\n',
        "description": "Generate and save images based on a user's query.",
        "secrets": {},
        "libraries": {},
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

    infer_gen = InferenceGenerator()
    implstr = r"""{
  "self": {
    "lm": null,
    "traces": [],
    "train": [],
    "demos": [
      {
        "augmented": true,
        "site": "providing data and insights for the global freight and logistics industry.",
        "conversation": "\nuser: EPA",
        "response": "The Environmental Protection Agency (EPA) recently fined Maritime International and its subsidiaries for violating federal laws related to the improper disposal of ammonia at facilities in Massachusetts and Connecticut.",
        "rationale": "produce the rating. We need to evaluate whether the response addresses the user's query about the EPA. The user simply mentioned \"EPA,\" which is quite broad and could refer to any recent activity or news related to the Environmental Protection Agency. The response provided specific information about a recent fine imposed by the EPA on Maritime International and its subsidiaries for violating federal laws related to ammonia disposal. This is relevant and provides a specific recent action taken by the EPA, which aligns with the user's broad query.",
        "rating": "Good",
      },
      {
        "site": "providing data and insights for the global freight and logistics industry.",
        "conversation": "\nuser: is Pete Buttigieg a good transporation secretary?\n \nbot: Pete Buttigieg has appointed Vinn White as the Federal Motor Carrier Safety Administration\u2019s deputy administrator.\nuser: what changes has he made?",
        "response": "Pete Buttigieg has appointed Vinn White as the Federal Motor Carrier Safety Administration\u2019s deputy administrator, focusing on enhancing safety for all roadway users.",
        "rating": "Good"
      }
    ],
    "signature_instructions": "Evaluate the response based on whether the response addresses the last question in the conversation for the site.\nPlease rate the response in following levels:\n- Good: The response fully addresses the question, with accurate and relevant information.\n- Bad: The response does not address the question, provides incorrect information, or is irrelevant.\n- Neutral: The response partially addresses the question but lacks some necessary details or clarity",
    "signature_prefix": "Rating[Good\/Bad\/Neutral]:",
    "extended_signature_instructions": "Evaluate the response based on whether the response addresses the last question in the conversation for the site.\nPlease rate the response in following levels:\n- Good: The response fully addresses the question, with accurate and relevant information.\n- Bad: The response does not address the question, provides incorrect information, or is irrelevant.\n- Neutral: The response partially addresses the question but lacks some necessary details or clarity",
    "extended_signature_prefix": "Rating[Good\/Bad\/Neutral]:"
  }
}"""
    try:
        implementation = json5.loads(implstr, strict=False)
    except json5.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        print(f"Error occurs at position {e.pos}")
        print(f"The problematic part of the JSON:")
        print(implstr[max(0, e.pos - 50) : e.pos + 50])

    infer_gen.add_fun(schema, PromptStrategyEnum.chain_of_thought, implementation)
    code = infer_gen.gen()

    print(code)
