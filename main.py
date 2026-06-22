import json
from pathlib import Path

import flet as ft

from VariablesViewModel import VariablesViewModel
from components.BitItem import BitItem
from components.CopyableTextField import CopyableTextField
from components.TableBlock import ColoredCompositeTable
from components.VariableItem import VariableItem


async def main(page: ft.Page):
    vm = VariablesViewModel()
    page.expand = True
    page.window.maximized = True

    list_container = ft.Column(spacing=10, expand=True, scroll=ft.ScrollMode.ALWAYS)
    total_bits_text = ft.Text(size=18, weight=ft.FontWeight.BOLD)
    table = ColoredCompositeTable(config_list=vm.structure_subject.value, group_by=8)
    table.listen_to_observable(vm.data_subject, page)

    writer = CopyableTextField(
        label="Writer",
        value="",
        multiline=True,
        options=vm.write_files.value,
        on_reload= vm.update_writers,
        on_style_change=vm.on_writer_option_change,
        on_is_cyclical=vm.on_writer_is_cyclical,
        on_function_title=vm.on_writer_function_title,
        on_padding=vm.on_writer_padding,
        on_struct_name=vm.on_writer_struct_name
    )
    reader = CopyableTextField(
        label="Reader",
        value="",
        multiline=True,
        options=vm.read_files.value,
        on_reload= vm.update_readers,
        on_style_change=vm.on_reader_option_change,
        on_is_cyclical=vm.on_reader_is_cyclical,
        on_function_title=vm.on_reader_function_title,
        on_padding=vm.on_reader_padding,
        on_struct_name=vm.on_reader_struct_name
    )

    numeral_system_8_item = ft.MenuItemButton(
        content="Octal",
        data="octal",
        on_click=lambda e: vm.change_numeral_system("octal")
    )
    numeral_system_16_item = ft.MenuItemButton(
        content="Hexadecimal (recommended)",
        data="hexadecimal",
        on_click=lambda e: vm.change_numeral_system("hexadecimal")
    )

    async def handle_import(e):
        files = await ft.FilePicker().pick_files(
            dialog_title="Select Configuration File",
            allowed_extensions=["json"]
        )
        if files and files[0].path:
            try:
                vm.import_from_file(files[0].path)
            except json.JSONDecodeError:
                show_error_dialog("The selected file is not a valid JSON file.")
            except ValueError as val_err:
                show_error_dialog(str(val_err))
            except Exception as ex:
                show_error_dialog(f"An unexpected error occurred:\n{str(ex)}")

    async def handle_export(e):
        file_path = await ft.FilePicker().save_file(
            dialog_title="Save Configuration As...",
            file_name="variables_config.json",
            allowed_extensions=["json"]
        )
        if file_path:
            vm.export_to_file(file_path)

    def show_clear_confirmation_dialog():
        def close_dialog(e):
            confirmation_dialog.open = False
            page.update()

        def confirm_clear(e):
            vm.clear_all_variables()  # Викликаємо очищення у ViewModel
            confirmation_dialog.open = False
            page.update()

        confirmation_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.WARNING_AMBER_ROUNDED, color=ft.Colors.ORANGE_700),
                ft.Text("Confirm Action")
            ], spacing=10),
            content=ft.Text("Are you sure you want to clear all variables? This action cannot be undone.", size=14),
            actions=[
                ft.TextButton("No", on_click=close_dialog),
                ft.ElevatedButton("Yes, Clear All", bgcolor=ft.Colors.RED_600, color=ft.Colors.WHITE,
                                  on_click=confirm_clear),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )

        page.overlay.append(confirmation_dialog)
        confirmation_dialog.open = True
        page.update()

    def show_error_dialog(message: str):
        def close_dialog(e):
            error_dialog.open = False
            page.update()

        error_dialog = ft.AlertDialog(
            title=ft.Row([
                ft.Icon(ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_700),
                ft.Text("Validation Error", color=ft.Colors.RED_700)
            ], spacing=10),
            content=ft.Text(message, size=14),
            actions=[
                ft.TextButton("OK", on_click=close_dialog)
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.overlay.append(error_dialog)
        error_dialog.open = True
        page.update()

    import_item = ft.MenuItemButton(
        content=ft.Row([ft.Icon(ft.Icons.DOWNLOAD, size=16), ft.Text("Import data")]),
        on_click=handle_import
    )

    export_item = ft.MenuItemButton(
        content=ft.Row([ft.Icon(ft.Icons.UPLOAD, size=16), ft.Text("Export data")]),
        on_click=handle_export
    )

    clear_all_item = ft.MenuItemButton(
        content=ft.Row([ft.Icon(ft.Icons.DELETE_FOREVER, size=16, color=ft.Colors.RED_600),
                        ft.Text("Clear All", color=ft.Colors.RED_600)]),
        on_click=lambda _: show_clear_confirmation_dialog()
    )

    menu_bar = ft.MenuBar(
        expand=True,
        style=ft.MenuStyle(alignment=ft.Alignment.TOP_LEFT),
        controls=[
            ft.SubmenuButton(
                content="Numeral system",
                controls=[numeral_system_8_item, numeral_system_16_item]
            ),
            ft.SubmenuButton(
                content="File",
                controls=[import_item, export_item, clear_all_item]
            )
        ]
    )

    vm.total_bits.subscribe(
        on_next=lambda bits: [
            setattr(total_bits_text, "value", f"Variables, bits: {bits}"),
            page.update()
        ]
    )

    vm.structure_subject.subscribe(
        on_next=lambda variables: [
            list_container.controls.clear(),
            [
                list_container.controls.append(
                    VariableItem(
                        variable=var,
                        on_swap_callback=vm.on_swap,
                        on_change_callback=vm.notify_data_change,
                        on_delete_callback=vm.remove_variable
                    ) if var.get("type") == "variable" else
                    BitItem(
                        variable=var,
                        on_swap_callback=vm.on_swap,
                        on_change_callback=vm.notify_data_change,
                        on_delete_callback=vm.remove_variable
                    )
                ) for var in variables
            ],
            page.update()
        ]
    )

    vm.numeral_system_subject.subscribe(
        on_next=lambda system: [
            setattr(numeral_system_8_item, "leading", ft.Icon(ft.Icons.CHECK, size=16) if system == "octal" else None),
            setattr(numeral_system_16_item, "leading",
                    ft.Icon(ft.Icons.CHECK, size=16) if system == "hexadecimal" else None),
            page.update()
        ]
    )

    page.add(
        ft.Column(
            expand=True,
            controls=[
                menu_bar,
                ft.Row(
                    expand=10,
                    controls=[
                        ft.Column(
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                            expand=1,
                            controls=[
                                total_bits_text,
                                list_container,
                                ft.Row(
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    controls=[
                                        ft.Button(
                                            content="Add new variable",
                                            icon=ft.Icons.PLUS_ONE,
                                            on_click=lambda e: vm.add_variable(),
                                        ),
                                        ft.Button(
                                            content="Add new additional bytes",
                                            icon=ft.Icons.DATA_OBJECT,
                                            on_click=lambda e: vm.add_bit(),
                                        )
                                    ]
                                )
                            ]
                        ),
                        ft.Column(
                            expand=2,
                            controls=[
                                ft.Container(
                                    content=ft.Text("Code", size=18, weight=ft.FontWeight.BOLD),
                                    alignment=ft.Alignment.CENTER
                                ),
                                ft.Column(
                                    expand=True,
                                    spacing=10,
                                    controls=[
                                        ft.Container(expand=1, content=writer),
                                        ft.Container(expand=1, content=reader)
                                    ]
                                )
                            ]
                        )
                    ]
                ),
                ft.Row(
                    expand=1,
                    scroll=ft.ScrollMode.ALWAYS,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            content=table,
                            expand=True,
                            alignment=ft.Alignment.CENTER,
                        )
                    ]
                )
            ]
        )
    )

    vm.generated_code_writer.subscribe(
        on_next=lambda data: [
            writer.set_value(data),
            page.update()
        ]
    )

    vm.generated_code_reader.subscribe(
        on_next=lambda data: [
            reader.set_value(data),
            page.update()
        ]
    )

    vm.notify_structure_change()

ft.run(main)