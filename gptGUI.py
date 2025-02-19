# gui_app.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QTextEdit,
    QPushButton, QLabel, QMessageBox
)
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt5.QtCore import Qt, QRegularExpression
from gptInterpreter import ChatGPTClient  # Ensure this module is in the same directory or PYTHONPATH

# ----------------- YAML Syntax Highlighter -----------------
class YAMLHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(YAMLHighlighter, self).__init__(parent)
        self.highlightingRules = []

        # Format for keys (words before a colon)
        keyFormat = QTextCharFormat()
        keyFormat.setForeground(QColor("blue"))
        keyPattern = QRegularExpression(r'^[\s-]*\w+(?=\s*:)')
        self.highlightingRules.append((keyPattern, keyFormat))

        # Format for booleans (true, false, yes, no)
        boolFormat = QTextCharFormat()
        boolFormat.setForeground(QColor("darkMagenta"))
        boolPattern = QRegularExpression(r'\b(true|false|yes|no)\b')
        self.highlightingRules.append((boolPattern, boolFormat))

        # Format for numbers
        numberFormat = QTextCharFormat()
        numberFormat.setForeground(QColor("darkCyan"))
        numberPattern = QRegularExpression(r'\b\d+(\.\d+)?\b')
        self.highlightingRules.append((numberPattern, numberFormat))

        # Format for comments (starting with #)
        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("green"))
        commentPattern = QRegularExpression(r'#.*')
        self.highlightingRules.append((commentPattern, commentFormat))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlightingRules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                match = it.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, fmt)
        self.setCurrentBlockState(0)

# ----------------- Main Window -----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChatGPT GUI")
        
        # Central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # API Key input box
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Enter your OpenAI API Key")
        layout.addWidget(QLabel("API Key:"))
        layout.addWidget(self.api_key_edit)
        
        # YAML prompt text box
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setPlaceholderText("Enter your YAML prompt here...")
        layout.addWidget(QLabel("Prompt (YAML syntax):"))
        layout.addWidget(self.prompt_edit)
        self.highlighter = YAMLHighlighter(self.prompt_edit.document())
        
        # Compile button
        self.compile_button = QPushButton("Compile")
        self.compile_button.clicked.connect(self.on_compile)
        layout.addWidget(self.compile_button)
        
        # Output text box for displaying the status
        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        layout.addWidget(QLabel("Output (Status):"))
        layout.addWidget(self.output_edit)

    def parse_status(self, response_text: str) -> str:
        """
        Parses the API response formatted as:
        "Status: ... Code: ..." and returns only the status portion.
        """
        if "Status:" in response_text and "Code:" in response_text:
            # Extract the portion between "Status:" and "Code:"
            status_part = response_text.split("Code:")[0]
            return status_part.replace("Status:", "").strip()
        else:
            # Fallback: return the full response if formatting isn't as expected
            return response_text.strip()

    def on_compile(self):
        api_key = self.api_key_edit.text().strip()
        prompt_text = self.prompt_edit.toPlainText().strip()
        
        if not api_key or not prompt_text:
            QMessageBox.warning(self, "Input Error", "Both API Key and prompt must be provided.")
            return

        try:
            # Create a ChatGPTClient with the provided API key
            client = ChatGPTClient(api_key=api_key)
            response = client.get_response(
                prompt_text=prompt_text,
                model="gpt-3.5-turbo",
                max_tokens=150,
                system_prompt="You are a knowledgeable assistant."
            )
            # Parse and display only the status part of the response
            parsed_status = self.parse_status(response)
            self.output_edit.setPlainText(parsed_status)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred:\n{str(e)}")

# ----------------- Main Application Entry -----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(600, 500)
    window.show()
    sys.exit(app.exec())
