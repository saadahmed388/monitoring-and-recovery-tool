from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QApplication, QShortcut, QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import Qt, QSize, QTimer
from utilities.sql_formatting import SqlPreview
from utilities.custom_widgets import StyledInputDialog
from datetime import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.managers.recovery_history_manager import RecoveryHistoryManager
    from utilities.stylesheets import StylingManager

class HistoryTab(QWidget):
    def __init__(self, recovery_history_manager: RecoveryHistoryManager, styling_manager: StylingManager):
        super().__init__()
        
        self.history_manager = recovery_history_manager
        self.styling_manager = styling_manager

        layout = QVBoxLayout()
        self.tree = QTreeWidget()        
        self.tree.setHeaderLabels(['Date', 'Env', 'Query Name', 'Pre Recovery', 'Post Recovery'])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(2, 500)
        self.tree.setColumnWidth(3, 250)
        self.tree.setColumnWidth(4, 250)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)
        self.setLayout(layout)
        
        self.history = self.history_manager.get_all_history()
        self.history_manager.history_updated.connect(self.load_history)
        self.load_history()
    
    def load_history(self):
        
        history = self.history_manager.get_all_history()
        
        self.tree.clear()
        item = QTreeWidgetItem()

        for date, d_items in (history or {}).items():
            for env, e_items in (d_items or {}).items():
                for name in (e_items or {}).keys():

                    item = QTreeWidgetItem([date, env, name, '', ''])
                    self.tree.addTopLevelItem(item)
        
                    pre_rec_preview_btn = QPushButton()
                    pre_rec_preview_btn.setIcon(QIcon("assets/g_circle.png"))
                    pre_rec_preview_btn.setFlat(True)
                    pre_rec_preview_btn.clicked.connect(lambda _, m = 'pre': self.show_table(m))
                    self.tree.setItemWidget(item, 3, pre_rec_preview_btn)

                    post_rec_preview_btn = QPushButton()
                    post_rec_preview_btn.setIcon(QIcon("assets/y_rectangle.png"))
                    post_rec_preview_btn.setFlat(True)
                    post_rec_preview_btn.clicked.connect(lambda _, m = 'post': self.show_table(m))
                    self.tree.setItemWidget(item, 4, post_rec_preview_btn)


    def show_table(self, mode):
        """Display the query result as a table in a popup."""
        
        curr_item = self.tree.currentItem()

        date = curr_item.text(0)
        env = curr_item.text(1)
        name = curr_item.text(2)

        rows = None

        if mode  == 'pre':
            rows = self.history[date][env][name]["pre_rec_data"]
        elif mode  == 'post':
            rows = self.history[date][env][name]["post_rec_data"]
        
        if not rows:
            QMessageBox.information(self, "No Data", "No rows available for this query.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle(f"{env} - {name}")
        dialog.resize(800, 400)

        layout = QVBoxLayout(dialog)

        table = QTableWidget(len(rows), len(rows[0]))
        table.setHorizontalHeaderLabels(list(rows[0].keys()))
        table.setStyleSheet(self.styling_manager.header_style())

        # Populate table
        for i, row in enumerate(rows):
            for j, col in enumerate(row.keys()):
                table.setItem(i, j, QTableWidgetItem(str(row[col])))

        table.resizeColumnsToContents()
        layout.addWidget(table)

        def copy_selected():
            selected_indexes = table.selectedIndexes()

            if not selected_indexes:
                return

            selected_indexes = sorted(selected_indexes, key=lambda x: (x.row(), x.column()))
            current_row = selected_indexes[0].row()
            row_data = []
            data = []

            for index in selected_indexes:
                if index.row() != current_row:
                    data.append("\t".join(row_data))
                    row_data = []
                    current_row = index.row()

                item = table.item(index.row(), index.column())
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")

            data.append("\t".join(row_data))

            QApplication.clipboard().setText("\n".join(data))

        shortcut = QShortcut(QKeySequence.Copy, table)
        shortcut.activated.connect(copy_selected)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        close_btn.setStyleSheet(self.styling_manager.button_style())

        layout.addWidget(close_btn)

        dialog.exec_()

            
            
