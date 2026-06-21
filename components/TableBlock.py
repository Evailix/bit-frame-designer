import flet as ft
import reactivex as rx

class TableBlock(ft.Column):
    def __init__(
            self,
            title: str,
            cells_count: int,
            cells_borders: list[ft.BorderSide],
            cell_width: int = 20,
            cell_height: int = 20,
            header_bg: str = ft.Colors.BLUE_GREY_100,
            cells_bg: str = ft.Colors.WHITE,
    ):
        super().__init__()
        self.spacing = 0
        self.cells_count = cells_count

        total_width = cell_width * cells_count

        self.header = ft.Container(
            content=ft.Text(title, weight=ft.FontWeight.BOLD, size=10, text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.BLACK, overflow=ft.TextOverflow.ELLIPSIS),
            alignment=ft.Alignment.CENTER,
            width=total_width,
            height=20,
            bgcolor=header_bg,
            border=ft.Border(
                bottom=ft.BorderSide(1, ft.Colors.BLACK),
                right=cells_borders[-1] if cells_borders else ft.BorderSide(1, ft.Colors.BLACK)
            )
        )

        self.text_controls = []
        cells = []

        for i in range(cells_count):
            txt = ft.Text("", size=11, weight=ft.FontWeight.W_500, color=ft.Colors.BLACK)
            self.text_controls.append(txt)

            right_border = cells_borders[i] if i < len(cells_borders) else ft.BorderSide(0.5, ft.Colors.BLACK)

            cells.append(
                ft.Container(
                    content=txt,
                    alignment=ft.Alignment.CENTER,
                    width=cell_width,
                    height=cell_height,
                    bgcolor=cells_bg,
                    border=ft.Border(right=right_border)
                )
            )

        self.cells_row = ft.Row(controls=cells, spacing=0)

        self.footer = ft.Container(
            content=ft.Text(
                f"{cells_count}b",
                size=9,
                color=ft.Colors.GREY_700,
                text_align=ft.TextAlign.CENTER
            ),
            alignment=ft.Alignment.CENTER,
            width=total_width,
            height=15
        )

        self.controls = [self.header, self.cells_row, self.footer]

    def update_cells(self, values: list):
        for i, txt_control in enumerate(self.text_controls):
            if i < len(values):
                txt_control.value = str(values[i])
            else:
                txt_control.value = ""


class ColoredCompositeTable(ft.Column):
    def __init__(self, config_list: list = None, group_by: int = 4):
        super().__init__()
        self.spacing = 5
        self.group_by = group_by

        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.table_row = ft.Row(
            controls=[],
            spacing=0,
            vertical_alignment=ft.CrossAxisAlignment.START
        )

        self.table_container = ft.Container(
            content=self.table_row,
            border=ft.Border.all(1, ft.Colors.BLACK),
            padding=0
        )

        self.total_bits_text = ft.Text(
            "",
            size=12,
            weight=ft.FontWeight.BOLD,
            text_align=ft.TextAlign.CENTER
        )

        self.controls = [self.table_container, self.total_bits_text]
        self.subscription = None

        if config_list:
            self.update_table(config_list)

    def listen_to_observable(self, observable: rx.Observable, page: ft.Page):
        if self.subscription:
            self.subscription.dispose()

        self.subscription = observable.subscribe(
            on_next=lambda config: self._handle_rx_update(config, page),
            on_error=lambda e: print(f"Rx Error: {e}")
        )

    def _handle_rx_update(self, config: list, page: ft.Page):
        self.update_table(config)
        page.update()

    def _parse_config(self, config_list: list) -> list:
        parsed_blocks = []
        for item in config_list:
            item_type = item.get("type", "variable")
            title = item.get("title", "")

            if item_type == "bit":
                base = int(item.get("base", 16))
                val_str = str(item.get("value", "0"))
                try:
                    int_val = int(val_str, base)
                    bin_val = bin(int_val)[2:]
                except ValueError:
                    bin_val = "0"

                count = int(item.get("count", len(bin_val)))
                if count < len(bin_val):
                    count = len(bin_val)

                bin_val = bin_val.zfill(count)
                values = list(bin_val)
            else:
                count_str = item.get("count", 0)
                count = int(count_str if count_str != "" else 0)
                values = []

            parsed_blocks.append({
                "title": title, "count": count, "values": values,
                "header_bg": item.get("header_bg", ft.Colors.BLUE_GREY_100),
                "cells_bg": item.get("cells_bg", ft.Colors.WHITE)
            })
        return parsed_blocks

    def update_table(self, config_list: list):
        parsed_blocks = self._parse_config(config_list)
        total_cells_in_table = sum(b["count"] for b in parsed_blocks)

        if total_cells_in_table == 0:
            self.table_row.controls.clear()
            self.total_bits_text.value = "0"
            return

        self.total_bits_text.value = f"{total_cells_in_table}"

        global_borders = []
        for abs_index in range(total_cells_in_table):
            is_absolute_last = (abs_index == total_cells_in_table - 1)
            if is_absolute_last:
                global_borders.append(ft.BorderSide(0, ft.Colors.TRANSPARENT))
            elif (abs_index + 1) % self.group_by == 0:
                global_borders.append(ft.BorderSide(2.5, ft.Colors.BLACK))
            else:
                global_borders.append(ft.BorderSide(0.5, ft.Colors.BLACK))

        self.table_row.controls.clear()
        cell_pointer = 0
        for index, block_data in enumerate(parsed_blocks):
            count = block_data["count"]
            block_borders = global_borders[cell_pointer: cell_pointer + count]
            cell_pointer += count

            block = TableBlock(
                title=block_data["title"], cells_count=count, cells_borders=block_borders,
                header_bg=block_data["header_bg"], cells_bg=block_data["cells_bg"]
            )
            block.update_cells(block_data["values"])
            self.table_row.controls.append(block)

    def will_unmount(self):
        if self.subscription:
            self.subscription.dispose()  # Чистимо ресурси Rx