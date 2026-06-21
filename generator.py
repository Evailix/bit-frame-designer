from collections import defaultdict
from pathlib import Path
from jinja2 import Template


def process_elements_to_context(
        function_name: str,
        items: list,
        array_base: int = 16,
        padding_bits: int = 0,
        is_cyclical: bool = False,
        struct_name: str = "PacketData"
) -> dict:
    if array_base not in (8, 16):
        raise ValueError("Підтримуються тільки 8 та 16 системи числення.")

    global_padding_bytes = padding_bits // 8
    intra_byte_bit_offset = padding_bits % 8

    processed_items = []
    for item in items:
        if item["type"] == "variable":
            processed_items.append(
                {"type": "variable", "name": item["title"], "bits": int(item["count"]), "is_static": False})
        elif item["type"] == "bit":
            base = int(item.get("base", 16))
            val_int = int(item["value"], base) if item["value"] else 0
            bits = max(1, val_int.bit_length())
            processed_items.append(
                {"type": "bit", "name": item["title"] or "static_bit", "bits": bits, "value_int": val_int,
                 "is_static": True})

    def get_c_type_bits(b):
        return 8 if b <= 8 else (16 if b <= 16 else (32 if b <= 32 else 64))

    seen_args = set()
    args = []
    for pi in processed_items:
        if not pi["is_static"] and pi["name"] not in seen_args:
            args.append({"name": pi["name"], "bits": pi["bits"], "type_bits": get_c_type_bits(pi["bits"])})
            seen_args.add(pi["name"])

    writer_bytes = defaultdict(lambda: {"ops": [], "static_val": 0})
    reader_fields = defaultdict(list)

    current_byte = 0
    current_bit = intra_byte_bit_offset

    for pi in processed_items:
        bits_left = pi["bits"]
        while bits_left > 0:
            bits_to_pack = min(bits_left, 8 - current_bit)
            val_shift = pi["bits"] - bits_left
            byte_shift = current_bit
            mask = (1 << bits_to_pack) - 1

            if pi["is_static"]:
                chunk = (pi["value_int"] >> val_shift) & mask
                writer_bytes[current_byte]["static_val"] |= (chunk << byte_shift)
            else:
                op_data = {"name": pi["name"], "val_shift": val_shift, "mask": mask, "mask_hex": f"0x{mask:02X}",
                           "mask_oct": f"0{mask:o}", "byte_shift": byte_shift}
                writer_bytes[current_byte]["ops"].append(op_data)

                reader_fields[pi["name"]].append({
                    "array_index": current_byte,
                    "mask": mask, "mask_hex": f"0x{mask:02X}", "mask_oct": f"0{mask:o}", "byte_shift": byte_shift,
                    "val_shift": val_shift
                })

            bits_left -= bits_to_pack
            current_bit += bits_to_pack
            if current_bit == 8:
                current_byte += 1
                current_bit = 0

    packet_size = current_byte + (1 if current_bit > 0 else 0)

    bytes_context = []
    for b_idx in sorted(writer_bytes.keys()):
        static_val = writer_bytes[b_idx]["static_val"]
        bytes_context.append({
            "index": b_idx, "operations": writer_bytes[b_idx]["ops"],
            "has_static": static_val > 0, "static_hex": f"0x{static_val:02X}", "static_oct": f"0{static_val:o}",
            "static_val": static_val
        })

    fields_context = [{"name": name, "parts": parts} for name, parts in reader_fields.items()]

    return {
        "function_name": function_name,
        "struct_name": struct_name,
        "is_cyclical": is_cyclical,
        "packet_size": packet_size,
        "global_padding_bytes": global_padding_bytes,
        "array_base": array_base,
        "args": args,
        "bytes": bytes_context,
        "fields": fields_context
    }

def generate_code(template_path: str, context: dict) -> str:
    template_content = Path(template_path).read_text(encoding="utf-8")
    return Template(template_content).render(**context)