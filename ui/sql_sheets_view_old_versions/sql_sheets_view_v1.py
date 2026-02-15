from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QTabWidget, QPushButton,
    QSizePolicy, QLabel, QComboBox, QTableWidget
)
from PyQt5.QtCore import Qt

class SQLSheetsWidget(QWidget):
    def __init__(self, db_clients, styling_manager=None):
        super().__init__()
        self.styling_manager = styling_manager
        self.db_clients = db_clients
        self._build_ui()

    def _build_ui(self):
        # Main horizontal layout: left column (button + vertical tabs) + right (editor area)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(12)

        # ---------- LEFT COLUMN ----------
        left_col = QWidget()
        left_col_layout = QVBoxLayout(left_col)
        left_col_layout.setContentsMargins(0, 0, 0, 0)
        left_col_layout.setSpacing(8)

        # New Sheet button (centered above tabs)
        self.new_sheet_btn = QPushButton("New Sheet")
        self.new_sheet_btn.setFixedHeight(36)
        # optional styling - replace with your styling_manager call
        self.new_sheet_btn.setStyleSheet("""
            QPushButton {
                background-color: #fafafa;
                color: #444;
                border: 1px solid #ddd;
                border-radius: 6px;
                padding: 6px 12px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #f2f2f2;
            }
        """)
        # Center the button in the left column
        left_col_layout.addWidget(self.new_sheet_btn, 0, Qt.AlignHCenter)

        # Vertical tabs (stacked)
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)   # vertical tabs on left of tab widget's content
        self.tabs.setMovable(True)
        # Make the tabbar narrow and the widget full height
        self.tabs.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.tabs.setFixedWidth(240)  # tune as needed for tab text width

        # Populate example tabs (replace with actual sheet pages)
        for i in range(1, 4):
            page = QLabel(f"Sheet {i} preview")   # replace with real sheet widget
            page.setAlignment(Qt.AlignCenter)
            self.tabs.addTab(page, f"Sheet {i}")

        left_col_layout.addWidget(self.tabs)

        # Make left column not expand horizontally (keeps width)
        left_col.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # ---------- RIGHT COLUMN (Editor / Results area) ----------
        right_col = QWidget()
        right_layout = QVBoxLayout(right_col)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(6)
        
        self.env_selector = QComboBox()
        self.env_selector.addItems(list(self.db_clients.keys()))
        
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton("Run")
        self.clear_btn = QPushButton("Clear")
        self.run_btn.setStyleSheet(self.styling_manager.button_style())
        self.clear_btn.setStyleSheet(self.styling_manager.button_style())
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.clear_btn)

        # Placeholder for editor area (replace with QPlainTextEdit, splitters etc)
        editor_placeholder = QLabel("SQL Editor area (replace with your editor + results)")
        editor_placeholder.setStyleSheet("background: #fff; border: 1px solid #eee;")
        editor_placeholder.setAlignment(Qt.AlignCenter)
        editor_placeholder.setMinimumWidth(600)
        editor_placeholder.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # --- Results Table ---
        result_table = QTableWidget()
        
        right_layout.addWidget(self.env_selector)
        right_layout.addWidget(editor_placeholder)
        right_layout.addLayout(btn_layout)
        right_layout.addWidget(result_table)

        # ---------- Add columns to main layout ----------
        main_layout.addWidget(left_col)   # left column with button + tabs
        main_layout.addWidget(right_col)  # main editor/results area

        # stretch: give right_col all remaining horizontal space
        main_layout.setStretch(0, 0)   # left column fixed
        main_layout.setStretch(1, 1)   # right column expands

        # connect button to behaviors
        self.run_btn.clicked.connect(lambda: self.run_sql(env_selector, editor_placeholder, result_table))
        self.clear_btn.clicked.connect(lambda: editor.clear())
        self.new_sheet_btn.clicked.connect(self.add_new_sheet)

    def add_new_sheet(self):
        # Example: add a new page/tab to the vertical tabs (replace with real sheet widget)
        count = self.tabs.count() + 1
        page = QLabel(f"Sheet {count} preview")
        page.setAlignment(Qt.AlignCenter)
        self.tabs.addTab(page, f"Sheet {count}")
        # Optionally select newly created sheet
        self.tabs.setCurrentIndex(self.tabs.count() - 1)


    def run_sql(self, env_selector, editor_placeholder, result_table):
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