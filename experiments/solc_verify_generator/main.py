import json
import subprocess
import os
import re
import string
import argparse
from typing import Tuple, Dict

SOLC = "solc"
SPEC_PATH = os.path.join("temp", "spec.sol_json.ast")


def call_solc(file_path):
    if os.path.isfile(SPEC_PATH):
        os.remove(SPEC_PATH)
    from subprocess import PIPE, run
    command = [SOLC, file_path, "--ast-compact-json", "-o", "temp"]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    return result


def process_annotations(annotations, state_variables, prefix):
    for key, value in annotations.items():
        processed_annotation = value
        if prefix:
            prefixed_value = add_prefix(value, state_variables, prefix)
            old_prefixed_value = remove_old_ref(prefixed_value, prefix)
            processed_annotation = old_prefixed_value

        annotations[key] = add_triple_bars(processed_annotation)


def add_prefix(annotation: str, state_variables: Dict[str, dict], prefix: str) -> str:
    for state_variable_name in state_variables.keys():
        annotation = annotation.replace(state_variable_name, prefix + "." + state_variable_name)
    return annotation


def remove_old_ref(annotation: str, prefix: str) -> str:
    pattern = r'__verifier_old_uint\s*\(\s*(nw.*?)\s*\)'
    replacement = lambda match: match.group(1).replace(prefix, f'{prefix}_old')
    return re.sub(pattern, replacement, annotation)


def add_triple_bars(value: str) -> str:
    lines = value.splitlines()
    new_annotation = ""
    for line in lines:
        new_annotation += "///" + line + "\n"
    return new_annotation


def generate_merge(spec: str, imp_template: str, merge_file_path: str, prefix: str = None):
    result = call_solc(spec)
    if result.returncode:
        # Something has gone wrong compiling the solidity code
        print("Something has gone wrong compiling the solidity code")
        raise RuntimeError(result.returncode, result.stdout + result.stderr)
    annotations, state_variables = parse_ast()
    process_annotations(annotations, state_variables, prefix)

    with open(imp_template, 'r') as impl_template_file:
        template_str = impl_template_file.read()
    template = string.Template(template_str)
    merge_contract = template.substitute(annotations)
    with open(merge_file_path, 'w') as merge_file:
        merge_file.write(merge_contract)


def parse_ast() -> Tuple[Dict[str, dict], Dict[str, dict]]:
    # Fixing this for simplicity for the time being
    annotations, state_variables = dict({}), dict({})
    with open(SPEC_PATH, 'r') as spec_file:
        spec_dict = json.load(spec_file)
        for node in spec_dict["nodes"]:
            if node["nodeType"] == "ContractDefinition":
                parse_contract(node, annotations, state_variables)

    return annotations, state_variables


def parse_contract(contract_json, annotations, state_variables):
    for node in contract_json["nodes"]:
        if node["nodeType"] == "FunctionDefinition":
            parse_function(node, annotations)
        if node["nodeType"] == "VariableDeclaration":
            parse_state_variable(node, state_variables)


def parse_state_variable(node_json, state_variables):
    name = node_json["name"]
    state_variables[name] = node_json


def parse_function(function_json, annotations):
    annotation = function_json["documentation"]
    name = function_json["name"]
    parameters_size = len(function_json["parameters"]["parameters"])
    annotations[name] = annotation # [$functionName] -> annotation (legacy)
    annotations[name + str(parameters_size)] = annotation # also: [$functionName + $numberOfParameters] -> annotation (for overloaded functions)


if __name__ == "__main__":
    parser = argparse.ArgumentParser("solc-verify contract generation")
    parser.add_argument("spec_file_path", help="The path to the specification file.", type=str)
    parser.add_argument("--prefix", help="The prefix to be added to each variable name in a spec annotation",
                        default=None, type=str)
    parser.add_argument("merge_template_file_path", help="The path to the merge template file.", type=str)
    parser.add_argument("merge_output_file_path", help="The path to the merge output file.", type=str)
    args = parser.parse_args()

    generate_merge(args.spec_file_path, args.merge_template_file_path, args.merge_output_file_path, prefix=args.prefix)
