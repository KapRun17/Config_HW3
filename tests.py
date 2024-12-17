import unittest
import subprocess
import sys


class TestConfigCompiler(unittest.TestCase):

    def run_main_with_input(self, input_data, output_file):
        """
        Вспомогательная функция для записи входных данных в файл и запуска main.py.
        Возвращает вывод из консоли.
        """
        # Создаем файл с входными данными
        with open('test.txt', 'w') as f:
            f.write(input_data)

        # Запуск main.py с использованием subprocess
        result = subprocess.run([sys.executable, 'main.py', '-i', 'test.txt', '-o', output_file],
                                capture_output=True, text=True)

        return result

    def test_valid_input(self):
        """
        Тест для корректного ввода, проверяет содержимое output.yaml.
        """
        input_data = """
        name is @"John"
        age is 30
        greeting is ?(name)
        items is [@"item1"; ?(age); 42;]
        """

        # Запуск main.py и получение вывода
        result = self.run_main_with_input(input_data, 'output.yaml')

        # Проверка, что ошибок в консоли не было
        self.assertNotIn("Error", result.stdout)

        # Проверка содержимого output.yaml
        with open('output.yaml', 'r') as f:
            output_content = f.read()

        # Проверка, что в output.yaml содержится ожидаемое значение
        self.assertIn("constants:", output_content)
        self.assertIn("name: John", output_content)
        self.assertIn("age: 30", output_content)
        self.assertIn("greeting: John", output_content)

        # Проверка содержимого списка 'items'
        self.assertIn("items:", output_content)
        self.assertIn("- item1", output_content)
        self.assertIn("- 30", output_content)
        self.assertIn("- 42", output_content)

    def test_invalid_reference(self):
        """
        Тест для некорректного ввода (неопределенная ссылка), проверяет вывод ошибки в консоли.
        """
        input_data = """
        greeting is ?(unknown_name)
        """

        # Запуск main.py и получение вывода
        result = self.run_main_with_input(input_data, 'output.yaml')

        # Проверка, что ошибка выводится в консоль
        self.assertIn("Error: Undefined reference: unknown_name", result.stderr)

    def test_invalid_syntax(self):
        """
        Тест для некорректного синтаксиса, проверяет, что ошибка не возникает в консоли,
        но проверяет содержимое output.yaml.
        """
        input_data = """
        name is @"John"
        age is 30
        greeting is ?(name)
        items is [@"item1"; 42
        """

        # Запуск main.py и получение вывода
        result = self.run_main_with_input(input_data, 'output.yaml')

        # Проверка, что в консоли не было ошибок
        self.assertNotIn("Error", result.stderr)

        # Проверка содержимого output.yaml на некорректные данные
        with open('output.yaml', 'r') as f:
            output_content = f.read()

        # Проверка, что output.yaml содержит частично обработанные данные
        self.assertIn("constants:", output_content)
        self.assertIn("name: John", output_content)
        self.assertIn("age: 30", output_content)
        self.assertIn("greeting: John", output_content)

    def test_missing_constant(self):
        """
        Тест для отсутствующей константы, проверяет вывод ошибки в консоли.
        """
        input_data = """
        greeting is ?(missing_constant)
        """

        # Запуск main.py и получение вывода
        result = self.run_main_with_input(input_data, 'output.yaml')

        # Проверка, что ошибка выводится в консоль
        self.assertIn("Error: Undefined reference: missing_constant", result.stderr)

    def test_single_line_comment(self):
        """
        Тест на однострочные комментарии (начинаются с 'C').
        """
        input_data = """
        C Это комментарий, который должен быть проигнорирован
        name is @"John"
        age is 30
        greeting is ?(name)
        """

        # Запуск main.py и получение вывода
        result = self.run_main_with_input(input_data, 'output.yaml')

        # Проверка, что ошибок в консоли не было
        self.assertNotIn("Error", result.stdout)

        # Чтение содержимого файла output.yaml
        with open('output.yaml', 'r') as f:
            output_content = f.read()

        # Диагностический вывод содержимого output.yaml
        print("Output content for single-line comment test:")
        print(output_content)

        # Убедиться, что однострочный комментарий не попал в output.yaml
        self.assertNotIn("C Это комментарий", output_content)

        # Проверка правильности содержимого
        self.assertIn("constants:", output_content)
        self.assertIn("name: John", output_content)
        self.assertIn("age: 30", output_content)
        self.assertIn("greeting: John", output_content)


    def test_multiline_comment(self):
        """
        Тест на многострочные комментарии (начинаются с '{{!' и заканчиваются на '}}').
        """
        input_data = """
        {{!
        Это многострочный комментарий
        который должен быть проигнорирован
        }}
        name is @"John"
        age is 30
        greeting is ?(name)
        """

        # Запуск main.py и получение вывода
        result = self.run_main_with_input(input_data, 'output.yaml')

        # Проверка, что ошибок в консоли не было
        self.assertNotIn("Error", result.stdout)

        # Чтение содержимого файла output.yaml
        with open('output.yaml', 'r') as f:
            output_content = f.read()

        # Диагностический вывод содержимого output.yaml
        print("Output content for multiline comment test:")
        print(output_content)

        # Убедиться, что многострочный комментарий не попал в output.yaml
        self.assertNotIn("{{! Это многострочный комментарий", output_content)

        # Проверка правильности содержимого
        self.assertIn("constants:", output_content)
        self.assertIn("name: John", output_content)
        self.assertIn("age: 30", output_content)
        self.assertIn("greeting: John", output_content)



if __name__ == '__main__':
    unittest.main()
