import json
from pathlib import Path

import flet as ft
from reactivex import operators as ops

from reactivex.subject import BehaviorSubject

from generator import generate_code, process_elements_to_context


def count_bits(variables_list: list) -> int:
    total = 0
    for item in variables_list:
        item_type = item.get("type", "variable")
        if item_type == "bit":
            base = int(item.get("base", 16))
            val_str = str(item.get("value", "0")).strip()
            if not val_str:
                val_str = "0"

            try:
                int_val = int(val_str, base)
                bin_val = bin(int_val)[2:]
            except ValueError:
                bin_val = "0"

            explicit_count = item.get("count")
            count = int(explicit_count) if (explicit_count and str(explicit_count).isdigit()) else len(bin_val)
            if count < len(bin_val):
                count = len(bin_val)

            total += count
        else:  # variable
            c = item.get("count", 0)
            total += int(c) if str(c).isdigit() else 0
    return total


def get_bits_needed(value: str, from_base: int) -> int:
    if value == "":
        return 0

    if not (2 <= from_base <= 16):
        raise ValueError()

    value_str = str(value).strip().upper()

    try:
        decimal_number = abs(int(value_str, from_base))
    except ValueError:
        raise ValueError()

    if decimal_number == 0:
        return 1

    return decimal_number.bit_length()


class VariablesViewModel:
    def __init__(self):
        self._variables = []

        self._readers = []
        self._writers = []

        self.structure_subject = BehaviorSubject(self._variables)
        self.data_subject = BehaviorSubject(self._variables)

        self.read_files = BehaviorSubject(self._readers)
        self.write_files = BehaviorSubject(self._writers)

        self.numeral_system_subject = BehaviorSubject("hexadecimal")

        self.total_bits = self.data_subject.pipe(
            ops.map(lambda vars: count_bits(vars))
        )
        self.update_readers()
        self.update_writers()

        self.generated_code_writer = BehaviorSubject("")
        self.generated_code_reader = BehaviorSubject("")

        self.reader_is_cyclical = False
        self.writer_is_cyclical = False

        self.writer_function_title = "default1"
        self.reader_function_title = "default1"

        self.writer_padding = 0
        self.reader_padding = 0

        self.writer_struct_name = "DefaultStruct"
        self.reader_struct_name = "DefaultStruct"




    def update_readers(self):
        dir_path = Path("readers")
        if dir_path.is_dir():
            files = [f.name for f in dir_path.glob("*.jinja2") if f.is_file()]
            self.read_files.on_next(files)
            self.selected_reader = files[0]
        else:
            self.read_files.on_next([])
            self.selected_reader = None

    def update_writers(self):
        dir_path = Path("writers")
        if dir_path.is_dir():
            files = [f.name for f in dir_path.glob("*.jinja2") if f.is_file()]
            self.write_files.on_next(files)
            self.selected_writer = files[0]
        else:
            self.write_files.on_next([])
            self.selected_writer = None

    def add_variable(self):
        new_var = {
            "type": "variable",
            "title": "",
            "count": "0"
        }
        self._variables.append(new_var)
        self.notify_structure_change()

    def add_bit(self):
        new_var = {
            "type": "bit",
            "title": "",
            "value": "",
            "base": 16
        }
        self._variables.append(new_var)
        self.notify_structure_change()

    def on_swap(self, src_variable: dict, target_variable: dict):
        if src_variable == target_variable:
            return
        try:
            idx_src = self._variables.index(src_variable)
            idx_target = self._variables.index(target_variable)

            moved_item = self._variables.pop(idx_src)
            self._variables.insert(idx_target, moved_item)
            self.notify_structure_change()
        except ValueError:
            pass

    def change_numeral_system(self, system: str):
        self.render_code()
        self.numeral_system_subject.on_next(system)

    def notify_structure_change(self):
        self.structure_subject.on_next(list(self._variables))
        self.data_subject.on_next(list(self._variables))

    def notify_data_change(self):
        self.render_code()
        self.data_subject.on_next(list(self._variables))


    def render_code(self):
        try:
            context = process_elements_to_context(
                function_name = self.writer_function_title,
                items = self._variables,
                array_base = 8 if self.numeral_system_subject.value == "octal" else 16,
                padding_bits = self.writer_padding,
                is_cyclical = self.writer_is_cyclical,
                struct_name=self.writer_struct_name
            )
            self.generated_code_writer.on_next(generate_code(f"writers/{self.selected_writer}", context=context).strip())
        except:
            self.generated_code_writer.on_next("Error generating code")

        try:
            context = process_elements_to_context(
                function_name = self.reader_function_title,
                items = self._variables,
                array_base = 8 if self.numeral_system_subject.value == "octal" else 16,
                padding_bits = self.reader_padding,
                is_cyclical = self.reader_is_cyclical,
                struct_name=self.reader_struct_name
            )
            self.generated_code_reader.on_next(generate_code(f"readers/{self.selected_reader}", context=context).strip())
        except:
            self.generated_code_reader.on_next("Error generating code")

    def on_reader_option_change(self, new_reader: str):
        self.selected_reader = new_reader
        self.notify_data_change()

    def on_writer_option_change(self, new_writer: str):
        self.selected_writer = new_writer
        self.notify_data_change()


    def on_reader_is_cyclical(self, new_value: bool):
        self.reader_is_cyclical = new_value
        self.notify_data_change()

    def on_writer_is_cyclical(self, new_value: bool):
        self.writer_is_cyclical = new_value
        self.notify_data_change()


    def on_reader_function_title(self, new_title: str):
        self.reader_function_title = new_title
        self.notify_data_change()

    def on_writer_function_title(self, new_title: str):
        self.writer_function_title = new_title
        self.notify_data_change()


    def on_writer_padding(self, new_padding: int):
        self.writer_padding = new_padding
        self.notify_data_change()

    def on_reader_padding(self, new_padding: int):
        self.reader_padding = new_padding
        self.notify_data_change()


    def on_writer_struct_name(self, new_name: str):
        self.writer_struct_name = new_name
        self.notify_data_change()


    def on_reader_struct_name(self, new_name: str):
        self.reader_struct_name = new_name

    def export_to_file(self, file_path: str):
        if not file_path:
            return

        with open(file_path, "w") as f:
            json.dump(self._variables, f, indent=4)

    def import_from_file(self, file_path: str):
        if not file_path:
            return

        with open(file_path, "r", encoding="utf-8") as f:
            variables_data = json.load(f)

        if not isinstance(variables_data, list):
            raise ValueError("Root element of the JSON must be a list.")

        for idx, item in enumerate(variables_data):
            if not isinstance(item, dict):
                raise ValueError(f"Element at index {idx} is not a valid object.")

            item_type = item.get("type")
            if item_type not in ["variable", "bit"]:
                raise ValueError(f"Element {idx} has an invalid type: '{item_type}'. Expected 'variable' or 'bit'.")

            if item_type == "variable":
                if "count" not in item:
                    raise ValueError(f"Element {idx} ('variable') is missing the 'count' field.")
                if not str(item["count"]).isdigit():
                    raise ValueError(f"Element {idx} has an invalid 'count' value. Must be a number.")

            elif item_type == "bit":
                if "value" not in item:
                    raise ValueError(f"Element {idx} ('bit') is missing the 'value' field.")
                if "base" not in item:
                    raise ValueError(f"Element {idx} ('bit') is missing the 'base' field.")
                if int(item.get("base", 16)) not in range(2, 17):
                    raise ValueError(f"Element {idx} has an unsupported 'base'")

        self._variables = variables_data
        self.notify_structure_change()

    def clear_all_variables(self):
        self._variables.clear()
        self.notify_structure_change()
        self.render_code()

    def remove_variable(self, variable: dict):
        if variable in self._variables:
            self._variables.remove(variable)
            self.notify_structure_change()
            self.render_code()