from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTabWidget, QPlainTextEdit, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, QComboBox, QListWidget
)
from PyQt5.QtCore import Qt

class SQLSheetsTab(QWidget):
    def __init__(self, db_clients, styling_manager):
        super().__init__()
        self.db_clients = db_clients
        self.styling_manager = styling_manager
        self.tab_bar()
        self.add_new_sheet()  # start with one sheet

    def tab_bar(self):
        left_col = QWidget()
        layout = QVBoxLayout(left_col)
        self.new_sheet_btn = QPushButton("New Sheet")   
        self.new_sheet_btn.setStyleSheet(self.styling_manager.button_style())
        layout.addWidget(self.new_sheet_btn)
        
        self.tabs = QListWidget()
        #self.tabs.setTabPosition(QTabWidget.West)  # vertical tabs
        layout.addWidget(self.tabs)
        self.setLayout(layout)
        self.new_sheet_btn.clicked.connect(lambda: self.add_new_sheet())
        
    def add_new_sheet(self):
        
        sheet = QWidget()
        vbox = QVBoxLayout()

        # --- Environment Selector ---
        env_selector = QComboBox()
        env_selector.addItems(list(self.db_clients.keys()))
        vbox.addWidget(env_selector)

        # --- SQL Editor ---
        editor = QPlainTextEdit()
        editor.setPlaceholderText("Write your SQL here...")
        vbox.addWidget(editor)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        run_btn = QPushButton("Run")
        clear_btn = QPushButton("Clear")
        btn_layout.addWidget(run_btn)
        btn_layout.addWidget(clear_btn)
        run_btn.setStyleSheet(self.styling_manager.button_style())
        clear_btn.setStyleSheet(self.styling_manager.button_style())
        vbox.addLayout(btn_layout)

        # --- Results Table ---
        result_table = QTableWidget()
        vbox.addWidget(result_table)

        sheet.setLayout(vbox)
        self.tabs.addItem(sheet, f"Sheet {self.tabs.count() + 1}")
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
        # --- Button Actions ---
        run_btn.clicked.connect(lambda: self.run_sql(env_selector, editor, result_table))
        clear_btn.clicked.connect(lambda: editor.clear())

    def run_sql(self, env_selector, editor, result_table):
        env = env_selector.currentText()
        sql = editor.toPlainText().strip()
        if not sql:
            return

        client = self.db_clients[env]
        try:
            rows = client.execute_select(sql)
            if not rows:
                result_table.clear()
                result_table.setRowCount(0)
                result_table.setColumnCount(0)
                return

            # Populate results
            headers = rows[0].keys()
            result_table.setColumnCount(len(headers))
            result_table.setHorizontalHeaderLabels(headers)
            result_table.setRowCount(len(rows))
            for i, row in enumerate(rows):
                for j, val in enumerate(row.values()):
                    result_table.setItem(i, j, QTableWidgetItem(str(val)))
        except Exception as e:
            result_table.setColumnCount(1)
            result_table.setRowCount(1)
            result_table.setHorizontalHeaderLabels(["Error"])
            result_table.setItem(0, 0, QTableWidgetItem(str(e)))
