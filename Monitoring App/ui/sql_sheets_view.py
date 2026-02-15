from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QStackedWidget,
    QPushButton, QTextEdit, QListWidgetItem, QTableWidget, QComboBox
)
from PyQt5.QtCore import Qt


class SQLSheetsTab(QWidget):
    def __init__(self, db_clients, styling_manager):
        super().__init__()
        self.db_clients = db_clients
        self.styling_manager = styling_manager

        # ==================== MAIN LAYOUT ====================
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(10)

        # ==================== LEFT PANEL ====================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(6)

        # “New Sheet” Button
        self.new_sheet_btn = QPushButton("＋ New Sheet")
        self.new_sheet_btn.setStyleSheet(self.styling_manager.button_style())
        self.new_sheet_btn.clicked.connect(self.add_new_sheet)
        left_layout.addWidget(self.new_sheet_btn)

        # Sheet List (Vertical Tab List)
        self.sheet_list = QListWidget()
        self.sheet_list.setStyleSheet(self.styling_manager.list_style())
        left_layout.addWidget(self.sheet_list, stretch=1)

        # ==================== RIGHT PANEL ====================
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(8)
        
        # --- Environment Selector ---
        env_selector = QComboBox()
        env_selector.addItems(list(self.db_clients.keys()))
        env_selector.setStyleSheet("""
            QComboBox {
                background-color: #fafafa;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                padding: 6px 10px;
                min-width: 180px;
                font-size: 9pt;
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
                color: #444;
            }
            QComboBox:hover {
                border: 1px solid #aaa;
            }
            QComboBox::drop-down {
                border-left: 1px solid #d0d0d0;
                width: 24px;
                background-color: #f2f2f2;
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
            }
            QComboBox::down-arrow {
                image: url(:/qt-project.org/styles/commonstyle/images/arrowdown-16.png);
                width: 12px;
                height: 12px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                background-color: #ffffff;
                selection-background-color: #e5e5e5;
                selection-color: #000;
                outline: none;
            }
        """)
        right_layout.addWidget(env_selector)

        # Stacked Widget → Displays the actual SQL Editors
        self.sheet_area = QStackedWidget()
        right_layout.addWidget(self.sheet_area)
        
        # --- Buttons ---
        btn_layout = QHBoxLayout()
        run_btn = QPushButton("Run")
        clear_btn = QPushButton("Clear")
        btn_layout.addWidget(run_btn)
        btn_layout.addWidget(clear_btn)
        run_btn.setStyleSheet(self.styling_manager.button_style())
        clear_btn.setStyleSheet(self.styling_manager.button_style())
        right_layout.addLayout(btn_layout)

        # --- Results Table ---
        result_table = QTableWidget()
        right_layout.addWidget(result_table)

        # ==================== ASSEMBLE ====================
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 4)

        # ==================== CONNECTIONS ====================
        self.sheet_list.currentRowChanged.connect(self.switch_sheet)

        # Add one default sheet
        self.add_new_sheet()

    # ==================== METHODS ====================

    def add_new_sheet(self):
        sheet_number = self.sheet_list.count() + 1
        sheet_name = f"Sheet {sheet_number}"

        # Create the text editor for this sheet
        editor = QTextEdit()
        editor.setPlaceholderText("-- Write your SQL query here --")
        editor.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #d0d0d0;
                border-radius: 6px;
                font-family: 'Segoe UI', 'Noto Sans', sans-serif;
                font-size: 9.5pt;
                color: #333;
                padding: 8px;
            }
        """)

        # Add to stack
        self.sheet_area.addWidget(editor)

        # Add to list
        item = QListWidgetItem(sheet_name)
        self.sheet_list.addItem(item)

        # Focus the new sheet
        self.sheet_list.setCurrentItem(item)

    def switch_sheet(self, index):
        """Switch displayed editor when a sheet is selected"""
        self.sheet_area.setCurrentIndex(index)

    def get_current_sql(self):
        """Return SQL from current sheet"""
        editor = self.sheet_area.currentWidget()
        return editor.toPlainText() if editor else ""

    def set_sql_in_current_sheet(self, text):
        """Set SQL text in current sheet"""
        editor = self.sheet_area.currentWidget()
        if editor:
            editor.setPlainText(text)
