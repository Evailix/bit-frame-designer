from pathlib import Path

import flet as ft


class CopyableTextField(ft.Column):
    def __init__(self, label="Text to copy", value="", expand=True, multiline=True, options=None, on_style_change=None,
                 on_reload=None, on_is_cyclical=None, on_function_title=None, on_padding=None, on_struct_name=None):

        super().__init__()
        self.expand = expand
        self.spacing = 5

        self.on_style_change_callback = on_style_change
        self.on_reload_callback = on_reload
        self.on_is_cyclical_callback = on_is_cyclical
        self.on_function_title_callback = on_function_title
        self.on_padding_callback = on_padding
        self.on_struct_name_callback = on_struct_name

        dropdown_options = [ft.dropdown.Option(text=opt, key=opt) for opt in options] if options else []
        self.style_dropdown = ft.Dropdown(
            label="Style",
            width=200,
            height=45,
            options=dropdown_options,
            value=options[0] if options else None,
            on_select=self._handle_style_change
        )

        self.function_name = ft.TextField(
            label="Function title",
            value="default1",
            max_lines = 1,
            multiline = False,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^(|[a-zA-Z_][a-zA-Z0-9_]*)$", replacement_string=""),
            on_change=self._handle_function_title_change,
            width=200
        )

        self.padding_in_bits = ft.TextField(
            label="Padding in bits",
            value="0",
            max_lines = 1,
            multiline = False,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            on_change=self._handle_padding_change,
            width = 100
        )

        self.struct_name = ft.TextField(
            label="Struct title",
            value="DefaultStruct",
            max_lines = 1,
            multiline = False,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^(|[a-zA-Z_][a-zA-Z0-9_]*)$", replacement_string=""),
            on_change=self._handle_struct_name_change,
            width=200
        )

        self.is_cyclical = ft.Switch(label="Is cyclical", value=False, on_change=self._handle_is_cyclical_change)

        self.reload_button = ft.IconButton(
            icon=ft.Icons.REFRESH,
            tooltip="Reload",
            icon_color=ft.Colors.GREEN,
            on_click=self._handle_reload
        )

        self.copy_button = ft.IconButton(
            icon=ft.Icons.COPY,
            tooltip="Copy to clipboard",
            icon_color=ft.Colors.BLUE,
            on_click=self.copy_to_clipboard
        )

        self.textfield = ft.TextField(
            disabled = True,
            label=label,
            value=value,
            expand=True,
            multiline=multiline,
        )

        self.scrollable_container = ft.Column(
            controls=[self.textfield],
            expand=True,
            scroll=ft.ScrollMode.ALWAYS
        )

        self.top_menu_row = ft.Row(
            alignment=ft.MainAxisAlignment.START,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                self.style_dropdown,
                self.function_name,
                self.padding_in_bits,
                self.struct_name,
                self.is_cyclical,
                self.reload_button,
                self.copy_button
            ]
        )

        self.controls = [
            self.top_menu_row,
            self.scrollable_container
        ]

    def update_options(self, new_options: list[str]):
        self.style_dropdown.options = [ft.dropdown.Option(opt) for opt in new_options]
        if self.style_dropdown.value not in new_options and new_options:
            self.style_dropdown.value = new_options[0]
        self.style_dropdown.update()

    def _handle_reload(self, e):
        if self.on_reload_callback:
            self.on_reload_callback(e)

    def _handle_style_change(self, e):
        if self.on_style_change_callback:
            self.on_style_change_callback(self.style_dropdown.value)


    def _handle_is_cyclical_change(self, e):
        if self.on_is_cyclical_callback:
            self.on_is_cyclical_callback(self.is_cyclical.value)

    def _handle_function_title_change(self, e):
        if self.on_function_title_callback:
            self.on_function_title_callback(self.function_name.value)

    def _handle_padding_change(self, e):
        if self.on_padding_callback:
            self.on_padding_callback(int(self.padding_in_bits.value) if self.padding_in_bits.value != "" else 0)


    def _handle_struct_name_change(self, e):
        if self.on_struct_name_callback:
            self.on_struct_name_callback(self.struct_name.value)

    def set_value(self, new_text: str):
        self.textfield.value = new_text
        if self.textfield.page is not None:
            self.textfield.update()

    def get_value(self) -> str:
        return self.textfield.value

    def get_selected_style(self) -> str:
        return self.style_dropdown.value

    async def copy_to_clipboard(self, e):
        text_to_copy = self.textfield.value
        await ft.Clipboard().set(text_to_copy)
        self.page.show_dialog(ft.SnackBar("Code copied to clipboard"))
        e.page.update()