# ================= ui/pending_view.py =================
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox, QHBoxLayout
from PyQt5.QtCore import Qt


class PendingTab(QWidget):
    def __init__(self, staging_manager, db_clients, query_manager, styling_manager):
        super().__init__()
        self.staging_manager = staging_manager
        self.db_clients = db_clients
        self.styling_manager = styling_manager
        self.query_manager = query_manager


        layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Env', 'Query', 'Row Data', 'Include', 'Status'])
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)

        
        
        
        
        # Create a horizontal bar for buttons
        button_bar = QHBoxLayout()     
        self.commit_btn = QPushButton('Commit All')
        self.revert_btn = QPushButton('Revert All')
        self.commit_btn.setStyleSheet(self.styling_manager.button_style())
        self.revert_btn.setStyleSheet(self.styling_manager.button_style())
        button_bar.addWidget(self.commit_btn)
        button_bar.addWidget(self.revert_btn)        
        layout.addLayout(button_bar)


        self.setLayout(layout)

        self.commit_btn.clicked.connect(self.commit_all)
        self.revert_btn.clicked.connect(self.revert_all)

    def refresh_tree(self):
        self.tree.clear()
        for s in self.staging_manager.staged_changes:
            item = QTreeWidgetItem([s['env'], s['query_name'], str(s['row_data']), '', s['status']])
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(3, Qt.Checked if s['include'] else Qt.Unchecked)
            self.tree.addTopLevelItem(item)


    def commit_all(self):
        self.staging_manager.commit_all(self.db_clients)
        self.refresh_tree()
        QMessageBox.information(self, 'Commit', 'Committed all included staged changes')


    def revert_all(self):
        self.staging_manager.revert_all(self.db_clients)
        self.refresh_tree()
        QMessageBox.information(self, 'Revert', 'Reverted committed changes')