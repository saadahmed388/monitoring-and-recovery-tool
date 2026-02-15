# ================= ui/recovery_templates_view.py =================
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog, QMessageBox, QHBoxLayout

class RecoveryTemplatesTab(QWidget):
    def __init__(self, staging_manager, query_manager, styling_manager):
        super().__init__()
        self.staging_manager = staging_manager
        self.styling_manager = styling_manager
        self.query_manager = query_manager

        layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Query Name', 'Recovery SQL Template'])
        self.tree.setColumnWidth(0, 250)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)

        # Create a horizontal bar for buttons
        button_bar = QHBoxLayout()
        self.edit_btn = QPushButton('Edit Recovery SQL Template')        
        self.edit_btn.setStyleSheet(self.styling_manager.button_style())
        button_bar.addWidget(self.edit_btn)
        layout.addLayout(button_bar)

        self.setLayout(layout)
        
        self.edit_btn.clicked.connect(self.edit_template)
        self.query_manager.queries_updated.connect(self.load_templates)
        self.load_templates()
        
        
    def edit_template(self):
        item = self.tree.currentItem()
        all_queries = self.query_manager.get_all_queries()
        if not item:
            QMessageBox.warning(self, 'Select', 'Select a query first')
            return
        name = item.text(0)
        template, ok = QInputDialog.getMultiLineText(self, 'Recovery SQL template', f'Edit template for {name}:', item.text(2))
        if ok:
            for q in all_queries:
                if (q["name"] == name):
                    if not template:
                        q["recovery_template"] = "No Recovery Template"
                    else:
                        q["recovery_template"] = template
                    self.query_manager.save_queries()
            QMessageBox.information(self, 'Updated', f'Recovery template for {name} updated')
    
    def load_templates(self):
        self.tree.clear()
        queries = self.query_manager.get_all_queries()
        if queries:
            for q in queries:
                name = q.get("name", "")
                recovery_template = q.get("recovery_template", "")
                item = QTreeWidgetItem([name, recovery_template])
                self.tree.addTopLevelItem(item)