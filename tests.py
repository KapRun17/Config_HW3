import subprocess
import tempfile
import unittest

class TestYamlProcessor(unittest.TestCase):

    def run_program(self, input_text, output_path):
        process = subprocess.run(
            ['python', 'main.py'],
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(process.stdout)
        return process

    def test_basic_translation(self):
        input_text = """
name: "John Doe"
age: 30
numbers:
  - 1
  - 2
  - 3
"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            process = self.run_program(input_text, temp_output.name)
            with open(temp_output.name, 'r', encoding='utf-8') as f:
                output = f.read()

    def test_comment_handling(self):
        input_text = """
# This is a comment
name: "Alice"
age: 25
numbers:
  - 10
  - 20
  - 30
"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            process = self.run_program(input_text, temp_output.name)
            with open(temp_output.name, 'r', encoding='utf-8') as f:
                output = f.read()

    def test_constant_evaluation(self):
        input_text = """
base: 10
height: 20
"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            process = self.run_program(input_text, temp_output.name)
            with open(temp_output.name, 'r', encoding='utf-8') as f:
                output = f.read()

    def test_array_syntax(self):
        input_text = """
items:
  - "apple"
  - "banana"
  - "cherry"
"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            process = self.run_program(input_text, temp_output.name)
            with open(temp_output.name, 'r', encoding='utf-8') as f:
                output = f.read()

    def test_error_handling(self):
        input_text = """
name: Invalid
"""
        with tempfile.NamedTemporaryFile(delete=False) as temp_output:
            process = self.run_program(input_text, temp_output.name)
            self.assertNotEqual(process.returncode, 0, msg="Программа должна завершиться с ошибкой")

if __name__ == '__main__':
    unittest.main()
