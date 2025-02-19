# Terminal YAML Editor with Code Execution

Welcome to the **Terminal YAML Editor** project! This project is a full-featured, terminal-based text editor built with Python’s `curses` library. It enables you to write YAML instructions that are interpreted and compiled into runnable Python code using the ChatGPT API (via a custom `gptInterpreter` module). The generated Python code can then be executed directly from within the editor. This project combines text editing, syntax highlighting, file operations, API key management, and direct code execution—all within a terminal interface.

---

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Usage](#usage)
- [Customization & Configuration](#customization--configuration)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

- **Terminal-Based Editor:**
  - Full-screen editor with line numbers and basic YAML syntax highlighting.
  - Manual cursor rendering (drawn as a highlighted block).
  - Two modes: **Insert mode** for editing and **Command mode** (triggered by pressing `;`) for executing commands.

- **ChatGPT Integration:**
  - Converts YAML instructions into fully functional, instantly runnable Python code.
  - Provides a detailed status message that includes explanations, design choices, and trade-offs made in the generated code.

- **Code Execution:**
  - Compile YAML to Python code, execute the generated code, and display the output within the terminal.
  - Command to save the generated Python code to a file (after removing markdown fences and commenting out any `Status:` lines).

- **File Operations:**
  - Open and save files from the current directory.
  - Save the current buffer as a file.
  - Manage API keys (prompt, save, delete, and re-enter).

- **Extensive Command Set:**
  - `;compile` — Compile your YAML into Python code.
  - `;execute` — Compile then immediately run the generated code.
  - `;run` — Execute the code from the last compile.
  - `;savepy <filename>` — Save the generated Python code to a file.
  - `;open <filename>` — Open a file.
  - `;save <filename>` — Save the current buffer.
  - `;deletekey` — Delete the stored API key.
  - `;rekey` — Re-enter a new API key.
  - `;help` — Display a help screen with available commands.
  - `;exit` — Exit the editor.

---

## Prerequisites

- **Python 3.6 or Newer:**  
  Ensure Python is installed on your machine.

- **Curses Library:**  
  This project uses Python's built-in `curses` module.  
  - On Unix-based systems, `curses` is typically pre-installed.
  - On Windows, install a compatible version such as [`windows-curses`](https://pypi.org/project/windows-curses/).

- **ChatGPT API Access:**  
  You will need an API key from OpenAI. This key is used by the `gptInterpreter` module to access ChatGPT.

---

## Installation & Setup

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/terminal-yaml-editor.git
   cd terminal-yaml-editor
   ```

2. **Install Dependencies:**

   - For Unix/Linux/macOS, the `curses` module is pre-installed.
   - For Windows, run:

     ```bash
     pip install windows-curses
     ```

3. **Configure the API Key:**

   - The first time you run the editor, you will be prompted to enter your API key.
   - The key is saved to a file named `apikey.txt` in the project directory.
   - To update or delete the API key later, use the `;rekey` or `;deletekey` commands in the editor.

4. **Configure `gptInterpreter`:**

   - Ensure that your `gptInterpreter.py` module is in the project directory.
   - This module handles interaction with the ChatGPT API using your API key.
   - Update the module as necessary to match any changes in the OpenAI API.

---

## Usage

1. **Start the Editor:**

   Run the main script:

   ```bash
   python terminal_editor.py
   ```

   A welcome message will appear; press any key twice to launch the editor.

2. **Editing Mode:**

   - The editor opens in **Insert mode**.
   - Use the arrow keys to navigate, type to insert text, and press **Enter** for a new line.
   - Line numbers and YAML syntax highlighting are enabled.

3. **Command Mode:**

   - Press `;` to switch to **Command mode**.
   - In this mode, you can type commands such as:
     - `;compile` — Compile your YAML into Python code.
     - `;execute` — Compile and immediately run the generated code.
     - `;run` — Run the code from the last compile.
     - `;savepy <filename>` — Save the generated Python code to a file.
     - `;open <filename>` — Open a file.
     - `;save <filename>` — Save the current buffer.
     - `;deletekey` — Delete the stored API key.
     - `;rekey` — Re-enter a new API key.
     - `;help` — Display a help screen with available commands.
     - `;exit` — Exit the editor.
   - The command prompt shows a disclaimer reminding you to type `;help` for commands.
   - To cancel command mode, press **ESC**.

4. **Compiling and Running Code:**

   - **Compile:** Use `;compile` to compile your YAML into Python code. A compile window displays the status (including detailed explanations of the generated code).
   - **Execute:** Use `;execute` to compile and then immediately run the generated code.
   - **Run:** Use `;run` to execute the code section from the last compile.
   - **Save Python Code:** Use `;savepy <filename>` to save the generated Python code (with markdown fences removed and any `Status:` lines commented out) to a file.

5. **Exiting the Editor:**

   - Use the command `;exit` in Command mode to close the editor.

---

## Customization & Configuration

- **System Prompt:**  
  The system prompt used for code generation is defined in the `SYSTEM_PROMPT` variable in `terminal_editor.py`. Modify this prompt if you wish to adjust how ChatGPT generates code or the detail included in the **Status:** message.

- **Color Schemes:**  
  Colors are defined in the `init_colors()` function. You can change the RGB values or color pair assignments to suit your preferences.

- **Editor Behavior:**  
  The editor’s behavior (cursor rendering, scrolling, key bindings, etc.) is managed in the `run_editor()` function. Adjust these interactions as needed.

- **Subprocess Timeout:**  
  The timeout for code execution is set to 10 seconds in the `run_code_section()` function. Adjust this if your code requires more time to execute.

---

## Troubleshooting

- **Blank Screen on Startup:**  
  If nothing appears until you press an arrow key, ensure that the editor is rendered once before entering the main loop. This is addressed by an initial render of the editor and command windows.

- **API Key Issues:**  
  - If the editor does not prompt for an API key, check that the `apikey.txt` file exists in the project directory.
  - Use `;deletekey` to remove a stored API key and `;rekey` to enter a new one.

- **Curses Errors:**  
  If you encounter curses-related errors, verify that your terminal supports the required features and that you are running the script in a proper terminal (not inside an IDE’s integrated terminal without curses support).

---

## Project Structure

```
terminal-yaml-editor/
├── terminal_editor.py       # Main editor script
├── gptInterpreter.py        # Module for interacting with the ChatGPT API
├── apikey.txt               # File where the API key is stored (created automatically)
└── README.md                # This README file
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```