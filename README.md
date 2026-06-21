# Bit Frame Designer 🚀

**Bit Frame Designer** is a visual desktop application designed for embedded systems developers, reverse engineers, and network protocol designers. It provides an intuitive GUI to construct binary data layouts (frames), mix fixed variables with raw dynamic bitfields, and instantly generate production-ready code.

Built using **Python**, **Flet** (Flutter-based GUI), and **ReactiveX (RxPY)** for a fully reactive, modern user experience.

---

## ✨ Features

* **Visual Frame Mapper:** See exactly how your data is distributed down to the single bit. Grouped visualization with custom boundaries (e.g., every 8 bits).
* **Mixed Data Types:** * `Variable`: Define traditional variables with custom bit sizes.
  * `Bit Field`: Input raw data in multiple bases (Hex, Dec, Oct, Bin) and see it parsed into bits in real-time.
* **Drag-and-Drop Reordering:** Easily rearrange fields within your frame using drag-and-drop handles.
* **Reactive UI:** No manual refreshes. Code generation, total bit calculation, and table layouts update instantly as you type.
* **Import/Export:** Save and load your configuration schemas via structured JSON files with built-in validation checks.
* **Template-Driven Code Generation:** Uses Jinja2 templates to generate modular Reader and Writer code on the fly.

---

## 🛠️ Architecture & Tech Stack

This project strictly follows the **MVVM (Model-View-ViewModel)** architectural pattern combined with **Reactive Extensions (Rx)** for clean state management:

* **Frontend:** [Flet](https://flet.dev/) (Flutter for Python)
* **State & Data Streams:** [ReactiveX (RxPY)](https://github.com/ReactiveX/RxPY)
* **Code Generation:** [Jinja2](https://jinja.palletsprojects.com/)
* **Format:** JSON schema validation

---

## 🚀 Getting Started

### Prerequisites
* Python 3.10 or higher

### Installation
1. Clone the repository:
   ```bash
   git clone [https://github.com/Evailix/bit-frame-designer.git](https://github.com/Evailix/bit-frame-designer.git)
   cd bit-frame-designer
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python main.py
   ```

---

## 📂 Configuration Schema (JSON)
When exporting or importing schemas, the tool validates the structure. Here is an example of a valid `variables_config.json`:
```json
[
    {
        "type": "bit",
        "title": "StatusFlags",
        "value": "A",
        "base": 16,
        "count": "4"
    },
    {
        "type": "variable",
        "title": "PayloadCounter",
        "count": "8"
    }
]
```

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Evailix/bit-frame-designer/issues).

---

## 📄 License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.
