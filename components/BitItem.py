import flet as ft


def convert_base(value: str, from_base: int, to_base: int) -> str:
    if not (2 <= from_base <= 16) or not (2 <= to_base <= 16):
        raise ValueError()

    value_str = str(value).strip().upper()
    try:
        decimal_number = int(value_str, from_base)
    except ValueError:
        return ""

    if decimal_number == 0:
        return "0"

    digits = "0123456789ABCDEF"
    result = ""

    while decimal_number > 0:
        remainder = decimal_number % to_base
        result = digits[remainder] + result
        decimal_number //= to_base

    return result


def generate_base_regex(base: int) -> str:
    if not (2 <= base <= 16):
        raise ValueError("Система числення має бути в діапазоні від 2 до 16.")

    if base <= 10:
        max_digit = base - 1
        return f"^[0-{max_digit}]*$"
    else:
        alphabet = "ABCDEF"
        max_letter = alphabet[base - 11]

        if base == 11:
            return "^[0-9Aa]*$"
        else:
            return f"^[0-9A-{max_letter}a-{max_letter.lower()}]*$"



class BitItem(ft.DragTarget):
    def __init__(self, variable: dict, on_swap_callback, on_change_callback, on_delete_callback):
        self.variable = variable
        self.on_swap_callback = on_swap_callback
        self.on_change_callback = on_change_callback
        self.on_delete_callback = on_delete_callback

        self.title_field = ft.TextField(
            value=self.variable.get("title", ""),
            label="Bit Title",
            max_lines=1, height=45, text_size=14, content_padding=10,
            on_change=self.handle_title_change,
            expand=True
        )

        self.value_field = ft.TextField(
            value=self.variable.get("value"),
            label="Value",
            max_lines=1, height=45, text_size=14, content_padding=10,
            on_change=self.handle_value_change,
            expand=True,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9A-Fa-f]*$", replacement_string=""),
        )

        dropdown_options = [ft.dropdown.Option(text=str(i), key=str(i)) for i in range(2, 17)]
        self.bits_field = ft.Dropdown(
            label="Base",
            height=45,
            text_size=14,
            content_padding=10,
            options=dropdown_options,
            value = "16",
            width=100,
            on_select=self.handle_bits_change,
        )
        self.delete_button = ft.IconButton(
            icon=ft.Icons.DELETE_OUTLINE,
            icon_color=ft.Colors.RED_200,
            tooltip="Delete element",
            on_click=lambda _: self.on_delete_callback(self.variable)
        )

        drag_source = ft.Draggable(
            group="vars",
            data=self.variable,
            expand=True,
            content=ft.Container(
                expand=True,
                content=ft.Row(
                    expand=True,
                    controls=[
                        self.title_field,
                        self.value_field,
                        ft.Text("size:"),
                        self.bits_field,
                        self.delete_button
                    ]
                ),
                bgcolor=ft.Colors.TEAL_800,
                padding=10,
                border_radius=5,
                width=400,
                alignment=ft.Alignment.CENTER,
            )
        )

        super().__init__(
            group="vars",
            content=drag_source,
            on_accept=self.handle_drop
        )

    def handle_title_change(self, e):
        self.variable["title"] = self.title_field.value
        self.on_change_callback()

    def handle_value_change(self, e):
        self.variable["value"] = self.value_field.value
        self.on_change_callback()

    def handle_drop(self, e: ft.DragTargetEvent):
        src_control = e.page.get_control(e.src_id)
        if src_control and hasattr(src_control, "data"):
            self.on_swap_callback(src_control.data, self.variable)
        self.on_change_callback()


    def handle_bits_change(self, e):
        new_base = int(self.bits_field.value)
        new_base_value = convert_base(self.variable["value"], self.variable["base"], new_base)
        self.variable["value"] = new_base_value
        self.value_field.value = new_base_value
        self.variable["base"] = new_base
        self.value_field.input_filter = ft.InputFilter(allow=True, regex_string=generate_base_regex(new_base), replacement_string="")
        self.on_change_callback()

