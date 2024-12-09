import re
import sys
import argparse
import yaml

def parse_args():
    parser = argparse.ArgumentParser(description="Tool to translate configuration language to YAML.")
    parser.add_argument("-o", "--output", type=str, required=True, help="Path to the output YAML file")
    return parser.parse_args()

def read_stdin():
    return sys.stdin.read()

def remove_comments(input_data):
    input_data = re.sub(r'C[^\n]*', '', input_data)  # Удаление однострочных комментариев
    input_data = re.sub(r'\{\{!\s*.*?\s*\}\}', '', input_data, flags=re.DOTALL)  # Удаление многострочных комментариев
    return input_data

def parse_constants(input_data):
    constants = {}
    matches = re.findall(r'([a-zA-Z][_a-zA-Z0-9]*)\s+is\s+((?:@"[^"]*"|\d+))', input_data)
    for name, value in matches:
        if value.startswith('@"') and value.endswith('"'):
            constants[name] = value[2:-1]  # Удаляем @" и "
        else:
            constants[name] = int(value)
    return constants

def resolve_constants(input_data, constants):
    def replace_constant(match):
        name = match.group(1)
        if name not in constants:
            raise ValueError(f"Undefined constant: {name}")
        return str(constants[name])

    return re.sub(r'\?\(([a-zA-Z][_a-zA-Z0-9]*)\)', replace_constant, input_data)

def parse_arrays(input_data):
    arrays = {}
    matches = re.findall(r'([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*\[([^\]]*)\]', input_data)
    for name, values in matches:
        arrays[name] = [value.strip() for value in values.split(';') if value.strip()]
    return arrays

def parse_to_dict(input_data):
    output = {}
    constants = parse_constants(input_data)
    input_data = resolve_constants(input_data, constants)
    output["constants"] = constants

    arrays = parse_arrays(input_data)
    output.update(arrays)
    matches = re.findall(r'([a-zA-Z][_a-zA-Z0-9]*)\s*=\s*(@"[^"]*"|\d+)', input_data)
    for name, value in matches:
        if value.startswith('@"') and value.endswith('"'):
            value = value[2:-1]
        else:
            value = int(value)
        output[name] = value

    return output

def main():
    args = parse_args()

    try:
        input_data = read_stdin()
        input_data = remove_comments(input_data)
        parsed_data = parse_to_dict(input_data)
        with open(args.output, 'w', encoding='utf-8') as output_file:
            yaml.dump(parsed_data, output_file, allow_unicode=True, sort_keys=False)

        print(f"Successfully converted to YAML. Output written to {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()