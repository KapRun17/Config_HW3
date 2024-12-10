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
	input_data = re.sub(r'C[^\n]*', '', input_data)
	input_data = re.sub(r'\{\{!\s*.*?\s*\}\}', '', input_data, flags=re.DOTALL)
	return input_data

def parse_constants(input_data):
	constants = {}
	matches = re.findall(r'([a-zA-Z][_a-zA-Z0-9]*)\s+is\s+((?:@"[^"]*"|\d+|\[[^\]]*\]))', input_data)
	for name, value in matches:
		if value.startswith('@"') and value.endswith('"'):
			constants[name] = value[2:-1]  # Удаляем @" и "
		elif value.startswith('[') and value.endswith(']'):
			constants[name] = parse_array(value)
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

def parse_array(array_str):
	# Удаление внешних скобок и разбиение на элементы
	array_str = array_str.strip()[1:-1]
	elements = []
	stack = []
	current = ""
	for char in array_str:
		if char == '[':
			stack.append(current)
			current = ""
		elif char == ']':
			if stack:
				sub_array = parse_array('[' + current + ']')
				current = stack.pop()
				elements.append(sub_array)
			else:
				raise ValueError(f"Unmatched closing bracket in array: {array_str}")
		elif char == ';' and not stack:
			elements.append(current.strip())
			current = ""
		else:
			current += char
	if current:
		elements.append(current.strip())
	return [parse_value(e) for e in elements]

def parse_value(value):
	if value.isdigit():
		return int(value)
	elif value.startswith('@"') and value.endswith('"'):
		return value[2:-1]
	elif value.startswith('[') and value.endswith(']'):
		return parse_array(value)
	else:
		raise ValueError(f"Invalid value: {value}")

def parse_to_dict(input_data):
	output = {}
	constants = parse_constants(input_data)
	input_data = resolve_constants(input_data, constants)
	output["constants"] = constants
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
