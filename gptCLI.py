#!/usr/bin/env python3
import curses
import curses.textpad
import re
import os
import subprocess
from gptInterpreter import ChatGPTClient

API_KEY_FILENAME = "apikey.txt"

# Define the system prompt once.
SYSTEM_PROMPT = """You are an advanced YAML-to-Python code converter. Your task is to:

1. Parse and Validate YAML: Thoroughly analyze the entire YAML input to ensure it is syntactically correct and that every specified feature is fully captured.
2. Error Reporting: If any syntax errors are found, immediately return a clear error message indicating the precise error and its corresponding line number. Do not output any Python code in this case.
3. Code Generation: If the YAML is valid, produce complete, efficient, and professionally structured Python code that runs instantly on the command line (no graphical interfaces). The generated code must fully implement all specified features without taking shortcuts or omitting any essential details, while being optimized to avoid unnecessary token overflow.
4. Strict Output Format: Your response must adhere exactly to the following format (no additional text is permitted):

Status: <state whether the YAML is correct or if errors were found; also indicate if Python code was generated>
Desc: <a one-line explanation of what the generated program does>
Next: <any required modifications such as API specifications, URLs, API keys, or module installations; if none, state 'None'>
Code: <the complete, syntactically correct Python code>
"""

def init_colors():
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_BLUE, -1)    # YAML keys
    curses.init_pair(2, curses.COLOR_YELLOW, -1)  # Command/instructions
    curses.init_pair(3, curses.COLOR_RED, -1)     # Errors
    curses.init_pair(4, curses.COLOR_GREEN, -1)   # Comments
    curses.init_pair(5, curses.COLOR_CYAN, -1)    # (Optional: other elements)
    # Line numbers in gray if possible; otherwise, white.
    if curses.can_change_color():
        curses.init_color(8, 500, 500, 500)  # Approximate gray
        curses.init_pair(6, 8, -1)
    else:
        curses.init_pair(6, curses.COLOR_WHITE, -1)

def highlight_line(win, y, line, offset=0):
    """
    Render a single line with rudimentary YAML syntax highlighting.
      - YAML keys (leading non-space text ending with a colon) appear in blue.
      - Comments (starting with '#') appear in green.
    Rendering begins at the given horizontal offset.
    """
    x = offset
    comment_index = line.find('#')
    if comment_index != -1:
        pre_comment = line[:comment_index]
        m = re.match(r'^(\s*\S+:)', pre_comment)
        if m:
            key_text = m.group(1)
            win.addstr(y, x, key_text, curses.color_pair(1))
            x += len(key_text)
            win.addstr(y, x, pre_comment[len(key_text):])
            x += len(pre_comment) - len(key_text)
        else:
            win.addstr(y, x, pre_comment)
            x += len(pre_comment)
        comment_text = line[comment_index:]
        win.addstr(y, x, comment_text, curses.color_pair(4))
    else:
        m = re.match(r'^(\s*\S+:)', line)
        if m:
            key_text = m.group(1)
            win.addstr(y, x, key_text, curses.color_pair(1))
            x += len(key_text)
            win.addstr(y, x, line[len(key_text):])
        else:
            win.addstr(y, x, line)

def get_user_input(stdscr, prompt):
    """
    Opens a temporary window to prompt the user for input.
    Returns the entered string.
    """
    height, width = stdscr.getmaxyx()
    win = curses.newwin(3, width - 4, height // 2 - 1, 2)
    win.border()
    win.addstr(1, 2, prompt, curses.color_pair(2))
    win.refresh()
    input_win = curses.newwin(1, width - len(prompt) - 10, height // 2, len(prompt) + 4)
    box = curses.textpad.Textbox(input_win)
    curses.curs_set(1)
    result = box.edit().strip()
    curses.curs_set(0)
    return result

def show_help(stdscr):
    """
    Display a help screen listing all available commands.
    """
    height, width = stdscr.getmaxyx()
    stdscr.clear()
    help_text = (
        "Available commands:\n"
        ";compile         - Compile the YAML via ChatGPTClient\n"
        ";execute         - Compile then immediately run the generated code\n"
        ";run             - Execute the code section from last compile\n"
        ";savepy <filename>- Save generated Python code (from last compile) to a file\n"
        ";open <filename>  - Open file from current directory\n"
        ";save <filename>  - Save current buffer to file\n"
        ";deletekey       - Delete the saved API key\n"
        ";rekey           - Re-enter and save a new API key\n"
        ";help            - Show this help message\n"
        ";exit            - Exit the editor\n"
        "\nPress any key to return to the editor."
    )
    lines = help_text.splitlines()
    for i, line in enumerate(lines):
        if i < height - 1:
            stdscr.addstr(i, 0, line)
    stdscr.refresh()
    stdscr.getch()
    stdscr.clear()

def run_code_section(stdscr, code_str):
    """
    Saves the provided code (assumed to be Python code) to a temporary file,
    after removing markdown code block markers, executes it, captures its output,
    and displays that output in the current window.
    Before saving, any header lines (Status:, Desc:, Next:) are filtered out.
    Press ';' to exit and return to the editor.
    """
    # Remove markdown code fences if present
    code_str = code_str.replace("```python", "").replace("```", "")
    
    # Filter out any header lines starting with "Status:", "Desc:", or "Next:"
    filtered_lines = []
    for line in code_str.splitlines():
        if re.match(r'^\s*(Status:|Desc:|Next:)', line):
            filtered_lines.append("#" + line)
        else:
            filtered_lines.append(line)
    code_str = "\n".join(filtered_lines)
    
    temp_filename = "temp_code.py"
    with open(temp_filename, "w") as f:
        f.write(code_str)
    try:
        result = subprocess.run(["python3", temp_filename],
                                capture_output=True, text=True, timeout=10)
        output = result.stdout + "\n" + result.stderr
    except Exception as e:
        output = f"Error executing code: {str(e)}"
    stdscr.clear()
    stdscr.addstr(0, 0, "Code Execution Output:", curses.color_pair(1))
    stdscr.addstr(2, 0, output)
    stdscr.addstr(curses.LINES - 1, 0, "Press ';' to return to the editor.", curses.color_pair(2))
    stdscr.refresh()
    while True:
        k = stdscr.getch()
        if k == ord(';'):
            break
    stdscr.clear()

def run_editor(stdscr, api_key):
    """
    Runs the full-screen YAML editor with line numbers, manual cursor drawing,
    and a command bar. Command mode is entered by pressing ";". Commands:
      ;compile         - Compile the YAML via ChatGPTClient.
      ;execute         - Compile then immediately run the generated code.
      ;run             - Execute the code section from last compile.
      ;savepy <filename>- Save generated Python code (from last compile) to a file.
      ;open <filename>  - Open file from current directory.
      ;save <filename>  - Save current buffer to file.
      ;deletekey       - Delete the saved API key.
      ;rekey           - Re-enter and save a new API key.
      ;help            - List available commands.
      ;exit            - Exit the editor.
    """
    stdscr.keypad(True)
    stdscr.clear()
    init_colors()
    height, width = stdscr.getmaxyx()
    editor_height = height - 1  # Reserve last line for command bar
    editor_win = curses.newwin(editor_height, width, 0, 0)
    editor_win.keypad(True)
    cmd_win = curses.newwin(1, width, editor_height, 0)

    line_no_width = 5  # Fixed width for line numbers

    # Initialize text buffer (list of lines)
    buffer = [""]
    cursor_y, cursor_x = 0, 0
    scroll_offset = 0

    # Last compile response stored for running code.
    last_compile_response = None

    # Modes: "insert" (normal editing) or "command" (entering a command)
    mode = "insert"
    command_str = ""
    
    # Render the editor once before entering the loop to fix initial blank display.
    editor_win.erase()
    editor_win.refresh()
    cmd_win.erase()
    cmd_win.refresh()

    while True:
        # Render editor area
        editor_win.erase()
        visible_lines = buffer[scroll_offset:scroll_offset+editor_height]
        for i, line in enumerate(visible_lines):
            # Draw line numbers in gray (right-aligned)
            line_number = i + scroll_offset + 1
            line_no = f"{line_number:>{line_no_width}} "  # e.g. "  1 "
            try:
                editor_win.addstr(i, 0, line_no, curses.color_pair(6))
            except curses.error:
                pass
            try:
                highlight_line(editor_win, i, line, offset=line_no_width + 1)
            except curses.error:
                pass

        # Manually draw the cursor as a block at its position
        cur_screen_y = cursor_y - scroll_offset
        cur_screen_x = cursor_x + line_no_width + 1
        if 0 <= cur_screen_y < editor_height and 0 <= cur_screen_x < width:
            try:
                editor_win.addch(cur_screen_y, cur_screen_x, ' ', curses.A_REVERSE)
            except curses.error:
                pass

        editor_win.refresh()

        # Render command bar depending on mode.
        cmd_win.erase()
        if mode == "insert":
            cmd_msg = "Insert mode (press ';' to enter command mode). Arrows: Navigate | Enter: New line | Backspace: Delete"
            cmd_win.addstr(0, 0, cmd_msg, curses.color_pair(2))
        elif mode == "command":
            disclaimer = "   (Command mode: type ;help for commands)"
            cmd_win.addstr(0, 0, command_str + disclaimer, curses.color_pair(2))
        cmd_win.refresh()

        key = stdscr.getch()

        if mode == "insert":
            if key == ord(';'):
                mode = "command"
                command_str = ";"
            elif key in (curses.KEY_BACKSPACE, 127):
                if cursor_x > 0:
                    line = buffer[cursor_y]
                    buffer[cursor_y] = line[:cursor_x-1] + line[cursor_x:]
                    cursor_x -= 1
                elif cursor_y > 0:
                    prev_line = buffer[cursor_y - 1]
                    current_line = buffer.pop(cursor_y)
                    cursor_y -= 1
                    cursor_x = len(prev_line)
                    buffer[cursor_y] = prev_line + current_line
            elif key in (curses.KEY_ENTER, 10, 13):
                line = buffer[cursor_y]
                new_line = line[cursor_x:]
                buffer[cursor_y] = line[:cursor_x]
                buffer.insert(cursor_y+1, new_line)
                cursor_y += 1
                cursor_x = 0
            elif key == curses.KEY_LEFT:
                if cursor_x > 0:
                    cursor_x -= 1
                elif cursor_y > 0:
                    cursor_y -= 1
                    cursor_x = len(buffer[cursor_y])
            elif key == curses.KEY_RIGHT:
                if cursor_x < len(buffer[cursor_y]):
                    cursor_x += 1
                elif cursor_y < len(buffer) - 1:
                    cursor_y += 1
                    cursor_x = 0
            elif key == curses.KEY_UP:
                if cursor_y > 0:
                    cursor_y -= 1
                    cursor_x = min(cursor_x, len(buffer[cursor_y]))
            elif key == curses.KEY_DOWN:
                if cursor_y < len(buffer) - 1:
                    cursor_y += 1
                    cursor_x = min(cursor_x, len(buffer[cursor_y]))
            elif 0 <= key <= 255:
                ch = chr(key)
                line = buffer[cursor_y]
                buffer[cursor_y] = line[:cursor_x] + ch + line[cursor_x:]
                cursor_x += 1
        elif mode == "command":
            if key in (curses.KEY_ENTER, 10, 13):
                command = command_str.lstrip(';').strip()
                if command == "":
                    mode = "insert"
                    command_str = ""
                    continue
                parts = command.split()
                cmd = parts[0].lower()
                args = parts[1:]
                if cmd == "execute":
                    yaml_prompt = "\n".join(buffer)
                    try:
                        client = ChatGPTClient(api_key=api_key)
                        response = client.get_response(
                            prompt_text=yaml_prompt,
                            system_prompt=SYSTEM_PROMPT
                        )
                        last_compile_response = response
                        # Parse the response into its header and code parts.
                        match = re.search(r"Status:\s*(.*?)\nDesc:\s*(.*?)\nNext:\s*(.*?)\nCode:\s*(.*)", response, re.DOTALL)
                        if match:
                            status_text = match.group(1).strip()
                            desc_text = match.group(2).strip()
                            next_text = match.group(3).strip()
                            header_text = f"Status: {status_text}\nDesc: {desc_text}\nNext: {next_text}"
                            code_section = match.group(4).strip()
                        else:
                            header_text = response.split("Code:")[0].strip() if "Code:" in response else response.strip()
                            code_section = response.split("Code:")[1].strip() if "Code:" in response else ""
                        stdscr.clear()
                        stdscr.addstr(0, 0, "Compile Result:", curses.color_pair(1))
                        stdscr.addstr(2, 0, header_text)
                        stdscr.addstr(height - 1, 0, "Press any key to execute the code.", curses.color_pair(2))
                        stdscr.refresh()
                        stdscr.getch()
                        if code_section:
                            run_code_section(stdscr, code_section)
                    except Exception as e:
                        stdscr.clear()
                        stdscr.addstr(0, 0, f"Error during execute: {str(e)}", curses.color_pair(3))
                        stdscr.addstr(height - 1, 0, "Press any key to return to the editor.", curses.color_pair(2))
                        stdscr.refresh()
                        stdscr.getch()
                elif cmd == "compile":
                    yaml_prompt = "\n".join(buffer)
                    try:
                        client = ChatGPTClient(api_key=api_key)
                        response = client.get_response(
                            prompt_text=yaml_prompt,
                            system_prompt=SYSTEM_PROMPT
                        )
                        last_compile_response = response
                        if "Code:" in response:
                            match = re.search(r"Status:\s*(.*?)\nDesc:\s*(.*?)\nNext:\s*(.*?)\nCode:\s*(.*)", response, re.DOTALL)
                            if match:
                                status_text = match.group(1).strip()
                                desc_text = match.group(2).strip()
                                next_text = match.group(3).strip()
                                header_text = f"Status: {status_text}\nDesc: {desc_text}\nNext: {next_text}"
                            else:
                                header_text = response.split("Code:")[0].strip()
                        else:
                            header_text = response.strip()
                        stdscr.clear()
                        stdscr.addstr(0, 0, "Compile Result:", curses.color_pair(1))
                        stdscr.addstr(2, 0, header_text)
                        stdscr.addstr(height - 1, 0, "Press any key to return to the editor.", curses.color_pair(2))
                        stdscr.refresh()
                        stdscr.getch()
                    except Exception as e:
                        stdscr.clear()
                        stdscr.addstr(0, 0, f"Error during compile: {str(e)}", curses.color_pair(3))
                        stdscr.addstr(height - 1, 0, "Press any key to return to the editor.", curses.color_pair(2))
                        stdscr.refresh()
                        stdscr.getch()
                elif cmd == "run":
                    if last_compile_response and "Code:" in last_compile_response:
                        match = re.search(r"Code:\s*(.*)", last_compile_response, re.DOTALL)
                        if match:
                            code_section = match.group(1).strip()
                        else:
                            code_section = ""
                        run_code_section(stdscr, code_section)
                    else:
                        cmd_win.erase()
                        cmd_win.addstr(0, 0, "No code section available from last compile.", curses.color_pair(3))
                        cmd_win.refresh()
                        stdscr.getch()
                elif cmd == "savepy" and args:
                    if last_compile_response and "Code:" in last_compile_response:
                        match = re.search(r"Code:\s*(.*)", last_compile_response, re.DOTALL)
                        if match:
                            code_section = match.group(1).strip()
                        else:
                            code_section = ""
                        # Remove markdown code fences if present
                        code_section = code_section.replace("```python", "").replace("```", "")
                        # Remove any header lines (Status:, Desc:, Next:) from the code section.
                        code_section = "\n".join(line for line in code_section.splitlines() if not re.match(r'^\s*(Status:|Desc:|Next:)', line))
                        filename = " ".join(args)
                        with open(filename, "w") as f:
                            f.write(code_section)
                        cmd_win.erase()
                        cmd_win.addstr(0, 0, f"Python code saved to '{filename}'.", curses.color_pair(1))
                        cmd_win.refresh()
                        stdscr.getch()
                    else:
                        cmd_win.erase()
                        cmd_win.addstr(0, 0, "No code available from last compile.", curses.color_pair(3))
                        cmd_win.refresh()
                        stdscr.getch()
                elif cmd == "open" and args:
                    filename = " ".join(args)
                    if os.path.exists(filename):
                        with open(filename, "r") as f:
                            content = f.read()
                        buffer = content.splitlines() or [""]
                        cursor_y, cursor_x = 0, 0
                    else:
                        cmd_win.erase()
                        cmd_win.addstr(0, 0, f"File '{filename}' not found.", curses.color_pair(3))
                        cmd_win.refresh()
                        stdscr.getch()
                elif cmd == "save" and args:
                    filename = " ".join(args)
                    with open(filename, "w") as f:
                        f.write("\n".join(buffer))
                    cmd_win.erase()
                    cmd_win.addstr(0, 0, f"Saved to '{filename}'.", curses.color_pair(1))
                    cmd_win.refresh()
                    stdscr.getch()
                elif cmd == "deletekey":
                    if os.path.exists(API_KEY_FILENAME):
                        os.remove(API_KEY_FILENAME)
                        cmd_win.erase()
                        cmd_win.addstr(0, 0, "API key file deleted.", curses.color_pair(3))
                        cmd_win.refresh()
                        stdscr.getch()
                        api_key = ""
                    else:
                        cmd_win.erase()
                        cmd_win.addstr(0, 0, "No API key file found.", curses.color_pair(3))
                        cmd_win.refresh()
                        stdscr.getch()
                elif cmd == "rekey":
                    new_key = get_user_input(stdscr, "Enter new API key: ")
                    if new_key:
                        api_key = new_key
                        with open(API_KEY_FILENAME, "w") as f:
                            f.write(api_key)
                        cmd_win.erase()
                        cmd_win.addstr(0, 0, "API key updated and saved.", curses.color_pair(1))
                        cmd_win.refresh()
                        stdscr.getch()
                elif cmd == "help":
                    show_help(stdscr)
                elif cmd == "exit":
                    return
                else:
                    cmd_win.erase()
                    cmd_win.addstr(0, 0, f"Unknown command: {command}", curses.color_pair(3))
                    cmd_win.refresh()
                    stdscr.getch()
                mode = "insert"
                command_str = ""
            elif key in (27,):  # ESC cancels command mode
                mode = "insert"
                command_str = ""
            elif key in (curses.KEY_BACKSPACE, 127):
                if len(command_str) > 1:
                    command_str = command_str[:-1]
            elif 0 <= key <= 255:
                command_str += chr(key)

        if cursor_y < scroll_offset:
            scroll_offset = cursor_y
        elif cursor_y >= scroll_offset + editor_height:
            scroll_offset = cursor_y - editor_height + 1

def main(stdscr):
    stdscr.keypad(True)
    curses.curs_set(0)  # Hide hardware cursor; we draw our own.
    init_colors()
    height, width = stdscr.getmaxyx()

    # Show welcome message
    stdscr.clear()
    welcome = "Welcome! Press any key twice to start the editor."
    stdscr.addstr(height // 2, (width - len(welcome)) // 2, welcome, curses.color_pair(2))
    stdscr.refresh()
    stdscr.getch()
    stdscr.clear()

    api_key = ""
    if os.path.exists(API_KEY_FILENAME):
        with open(API_KEY_FILENAME, "r") as f:
            api_key = f.read().strip()

    if not api_key:
        key_win = curses.newwin(3, width, 0, 0)
        key_win.border()
        key_win.addstr(0, 2, " API Key ")
        key_win.addstr(1, 1, "Enter API Key: ")
        key_win.refresh()
        api_input_win = curses.newwin(1, width - 20, 1, 17)
        api_box = curses.textpad.Textbox(api_input_win)
        curses.curs_set(1)
        api_key = api_box.edit().strip()
        with open(API_KEY_FILENAME, "w") as f:
            f.write(api_key)

    run_editor(stdscr, api_key)

if __name__ == "__main__":
    curses.wrapper(main)
