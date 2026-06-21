import flet as ft

class VariableItem(ft.DragTarget):
    def __init__(self, variable: dict, on_swap_callback, on_change_callback, on_delete_callback):
        self.variable = variable
        self.on_swap_callback = on_swap_callback
        self.on_change_callback = on_change_callback
        self.on_delete_callback = on_delete_callback

        self.title_field = ft.TextField(
            value=self.variable.get("title"),
            label="Title in code",
            max_lines=1,
            height=45,
            text_size=14,
            content_padding=10,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^(|[a-zA-Z_][a-zA-Z0-9_]*)$", replacement_string=""),
            on_change=self.handle_text_change,
            expand=True
        )

        self.bits_field = ft.TextField(
            value=str(self.variable.get("count")),
            label="Bits",
            max_lines=1,
            height=45,
            text_size=14,
            content_padding=10,
            keyboard_type=ft.KeyboardType.NUMBER,
            input_filter=ft.InputFilter(allow=True, regex_string=r"^[0-9]*$", replacement_string=""),
            hint_text = "0",
            on_change=self.handle_numeric_change,
            expand=True
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
                expand = True,
                content=ft.Row(
                    expand=True,
                    controls = [
                        self.title_field,
                        ft.Text("->"),
                        self.bits_field,
                        self.delete_button
                    ]
                ),
                bgcolor=ft.Colors.BLUE_GREY_700,
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

    def handle_text_change(self, e):
        self.variable["title"] = self.title_field.value
        self.on_change_callback()

    def handle_numeric_change(self, e):
        self.variable["count"] = self.bits_field.value
        self.on_change_callback()

    def handle_drop(self, e: ft.DragTargetEvent):
        src_control = e.page.get_control(e.src_id)

        if src_control and hasattr(src_control, "data"):
            src_obj = src_control.data
            self.on_swap_callback(src_obj, self.variable)

        self.on_change_callback()