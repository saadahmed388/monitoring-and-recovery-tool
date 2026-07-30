from PyQt5.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QDialog
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont, QTextCursor
from PyQt5.QtCore import Qt, QRegExp
from utilities.stylesheets import StylingManager
import sys


class SqlHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super(SqlHighlighter, self).__init__(parent)

        # --- Define text formats ---
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#0077cc"))
        keyword_format.setFontWeight(QFont.Bold)

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#d14"))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#098658"))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#888888"))
        comment_format.setFontItalic(True)

        # --- Regex rules ---
        self.rules = []

        keywords = [
            "SELECT", "FROM", "WHERE", "AND", "OR", "INSERT", "UPDATE", "DELETE",
            "CREATE", "ALTER", "DROP", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER",
            "GROUP", "BY", "ORDER", "HAVING", "AS", "ON", "INTO", "VALUES", "NOT", "NULL"
        ]

        for kw in keywords:
            pattern = QRegExp(rf"\b{kw}\b")
            pattern.setCaseSensitivity(Qt.CaseInsensitive)
            self.rules.append((pattern, keyword_format))

        # Strings
        self.rules.append((QRegExp("'[^']*'"), string_format))

        # Numbers
        self.rules.append((QRegExp(r"\b[0-9]+\b"), number_format))

        # Comments (single-line)
        self.rules.append((QRegExp(r"--[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.rules:
            i = pattern.indexIn(text)
            while i >= 0:
                length = pattern.matchedLength()
                self.setFormat(i, length, fmt)
                i = pattern.indexIn(text, i + length)


class SqlPreview(QMainWindow):
    def __init__(self, sql_text):
        super().__init__()
        self.setWindowTitle("SQL Preview")
        self.resize(700, 500)

        editor = QPlainTextEdit()
        editor.setStyleSheet("QPlainTextEdit { background-color: #f9f9f9; color: #222; }")
        editor.setPlainText(sql_text)
        editor.setReadOnly(True)
        editor.setFont(QFont("Consolas", 11))

        # ✅ Attach syntax highlighter AFTER setting text
        self.highlighter = SqlHighlighter(editor.document())

        self.setCentralWidget(editor)

class SqlPreviewV2(QDialog):
    def __init__(self, sql_text, mode, edit_func = None, save_func = None, parent = None):
        super().__init__(parent)

        self.setWindowTitle("SQL Preview")
        self.resize(700, 500)

        self.styling_manager = StylingManager()
        self.edit_func = edit_func
        self.save_func = save_func
        self.sql_text = sql_text
        self.mode = mode
        self.active = False

        self.editor = QPlainTextEdit()
        self.editor.setPlainText(sql_text)
        self.editor.setStyleSheet("QPlainTextEdit { background-color: #f9f9f9; color: #222; }")
        self.editor.setFont(QFont("Consolas", 11))
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.editor)
        self.layout_bridge = layout
        self.highlighter = SqlHighlighter(self.editor.document())

    def preview_mode(self):
        self.editor.setReadOnly(True)
        edit_btn = QPushButton('Edit')
        edit_btn.setStyleSheet(self.styling_manager.button_style())
        edit_btn.clicked.connect(lambda : self.edit_func(self.sql_text, self.mode))
        btn_bar_layout = QHBoxLayout()
        btn_bar_layout.addWidget(edit_btn)
        self.layout_bridge.addLayout(btn_bar_layout)
        self.active = True
        self.show()
    
    def edit_mode(self):
        self.editor.setReadOnly(False)
        save_btn = QPushButton('Save Changes')
        save_btn.setStyleSheet(self.styling_manager.button_style())
        save_btn.clicked.connect(lambda _ : self.handle_save(self.mode))
        btn_bar_layout = QHBoxLayout()
        btn_bar_layout.addWidget(save_btn)
        self.layout_bridge.addLayout(btn_bar_layout)
        self.active = True
        self.show()

    def handle_save(self, mode):
        text = self.editor.toPlainText()
        self.save_func(text, mode)

        