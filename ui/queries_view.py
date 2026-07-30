# ---------------- ui/queries_view.py ----------------
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QInputDialog,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout, QApplication
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize, QTimer
from utilities.sql_formatting import SqlPreview
from utilities.custom_widgets import StyledInputDialog
from datetime import datetime
from core.managers.query_manager import QueryManager

class QueriesTab(QWidget):
    def __init__(self, db_clients, staging_manager, query_manager: QueryManager, styling_manager):
        super().__init__()
        self.db_clients = db_clients
        self.staging_manager = staging_manager
        self.query_manager = query_manager
        self.styling_manager = styling_manager

        layout = QVBoxLayout()
        self.tree = QTreeWidget()        
        self.tree.setHeaderLabels(['Active', 'Auto Recovery', 'Query Name', 'SQL', 'Added On', 'Last Modified On'])
        self.tree.setColumnWidth(0, 100)
        self.tree.setColumnWidth(1, 150)
        self.tree.setColumnWidth(2, 450)
        self.tree.setColumnWidth(4, 200)
        self.tree.setColumnWidth(5, 2000)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)
        
        # Create a horizontal bar for buttons
        button_bar = QHBoxLayout()

        self.move_up_btn = QPushButton()
        self.move_up_btn.setIcon(QIcon("assets/triangle_up.svg"))
        self.move_up_btn.setIconSize(QSize(50, 50))
        self.move_up_btn.setFixedSize(60, 60)
        
        self.move_down_btn = QPushButton()
        self.move_down_btn.setIcon(QIcon("assets/down_expand.svg"))
        self.move_down_btn.setIconSize(QSize(50, 50))
        self.move_down_btn.setFixedSize(60, 60)
        
        self.add_btn = QPushButton('Add Monitoring SQL')
        self.modify_btn = QPushButton('Modify SQL')
        self.delete_btn = QPushButton('Delete SQL')
        self.activate_all_btn = QPushButton('Activate All')
        self.deactivate_all_btn = QPushButton('Deactivate All')
        
        button_bar.addWidget(self.move_up_btn)
        button_bar.addWidget(self.move_down_btn)
        button_bar.addWidget(self.add_btn)
        button_bar.addWidget(self.modify_btn)
        button_bar.addWidget(self.delete_btn)
        button_bar.addWidget(self.activate_all_btn)
        button_bar.addWidget(self.deactivate_all_btn)
        
        self.activate_all_btn.setStyleSheet(self.styling_manager.button_style())
        self.deactivate_all_btn.setStyleSheet(self.styling_manager.button_style())
        self.add_btn.setStyleSheet(self.styling_manager.button_style())
        self.modify_btn.setStyleSheet(self.styling_manager.button_style())
        self.delete_btn.setStyleSheet(self.styling_manager.button_style())
        
        layout.addLayout(button_bar)
              
        self.setLayout(layout)
        
        self.sql_queries = {}        
        self.add_btn.clicked.connect(self.add_query)
        self.modify_btn.clicked.connect(self.modify_query)
        self.delete_btn.clicked.connect(self.delete_query)
        self.move_up_btn.clicked.connect(self.move_up)
        self.move_down_btn.clicked.connect(self.move_down)
        self.activate_all_btn.clicked.connect(self.activate_all_queries)
        self.deactivate_all_btn.clicked.connect(self.deactivate_all_queries)
        self.query_manager.queries_updated.connect(self.load_queries)
        self.tree.itemChanged.connect(self.on_activity_state_change)
        self.load_queries()
               
    def activate_all_queries(self):
        queries = self.query_manager.get_all_queries()
        for q in queries:
            q["active"] = "Y"
        self.query_manager.save_queries()
        self.query_manager.load_queries()

    def deactivate_all_queries(self):
        queries = self.query_manager.get_all_queries()
        for q in queries:
            q["active"] = "N"
        self.query_manager.save_queries()
        self.query_manager.load_queries()

    def on_activity_state_change(self, item: QTreeWidgetItem, column):        
        if column not in (0,1):
            return
        self.tree.blockSignals(True)
        try:
            queries = self.query_manager.get_all_queries()            
            name = item.text(2)
            match column:
                case 0:
                    state = item.checkState(0)
                    active = "Y" if state == Qt.Checked else "N"
                    for q in queries:
                        if q["name"] == name:
                           q["active"] = active
                           break 
                case 1:
                    state = item.checkState(1)
                    auto_recovery = "Y" if state == Qt.Checked else "N"
                    for q in queries:
                        if q["name"] == name:
                           q["auto_recovery"] = auto_recovery
                           break 
        finally:
            self.tree.blockSignals(False)
        
        QTimer.singleShot(0, self.query_manager.save_queries)
        QTimer.singleShot(0, self.query_manager.load_queries)

    def add_query(self):
        name, ok1 = StyledInputDialog('Query Name', 'Enter monitoring query name:').get_text()        
        if not ok1 or not name:
            return
        sql, ok2 = StyledInputDialog('SQL', 'Enter monitoring SQL:', num_lines = "M").get_text()
        if not ok2 or not sql:
            return
        self.query_manager.add_query(name, sql)
        QMessageBox.information(self, 'Added', f'Query {name} added')
    
    def modify_query(self):
        selected = self.tree.currentItem()
        
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a query to edit.")
            return
        
        queries = self.query_manager.get_all_queries()
        old_name = selected.text(2)
        for q in queries: 
            if q["name"] == old_name: 
                old_sql = q["sql"]
                            
        new_name, ok1 = StyledInputDialog('Query Name', 'Modify query name:', default_text = old_name).get_text()
        new_sql, ok2 = StyledInputDialog('SQL', 'Enter monitoring SQL:', default_text = old_sql, num_lines = "M").get_text()
        
        for q in queries:
            if q["name"] == old_name and q["sql"] == old_sql:
                if(new_name != old_name or new_sql != old_sql):
                    q["date_modified_on"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                if ok1 and new_name.strip():
                    q["name"] = new_name.strip()
                if ok2 and new_sql.strip():
                    q["sql"] = new_sql.strip()
                break

        self.query_manager.save_queries()
        self.query_manager.load_queries() 
        
        
    def delete_query(self):
        selected = self.tree.currentItem()
        if not selected:
            QMessageBox.warning(self, "No Selection", "Please select a query to delete.")
            return
        
        name = selected.text(2)
        
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete query '{name}'?",
            QMessageBox.Yes | QMessageBox.No
        )
        if confirm != QMessageBox.Yes:
            return

        self.query_manager.delete_query(name)
        self.query_manager.save_queries()
        self.query_manager.load_queries()
        
    def load_queries(self):
        self.tree.clear()
        queries = self.query_manager.get_all_queries()
        if queries:
            for q in queries:
                name = q.get("name", "")
                sql = q.get("sql", "")
                active = q.get("active", "")
                auto_recovery = q.get("auto_recovery", "")
                date_added_on = q.get("date_added_on", "")
                date_modified_on = q.get("date_modified_on", "")
                
                self.sql_queries[name] = sql
                
                item = QTreeWidgetItem(['', '', name, '', date_added_on, date_modified_on])
                self.tree.addTopLevelItem(item)
                
                # Active Flag
                self.tree.blockSignals(True)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Checked if active == "Y" else Qt.Unchecked)
                item.setCheckState(1, Qt.Checked if auto_recovery == "Y" else Qt.Unchecked)
                self.tree.blockSignals(False)
                    
                # Preview button
                preview_btn = QPushButton()
                preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                preview_btn.setFlat(True)
                preview_btn.clicked.connect(lambda _, q=name: self.show_sql(q))
                self.tree.setItemWidget(item, 3, preview_btn)

    def show_sql(self, q_name):
        self.preview_window = SqlPreview(self.sql_queries[q_name])
        self.preview_window.show()
        
    
    def get_active_queries(self):
        QApplication.processEvents()
        self.active_queries = set()
        for i in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(i)
            if item.checkState(0) == Qt.Checked:
                query_name = item.text(2)
                self.active_queries.add(query_name)
        
        return self.active_queries
        
    def move_up(self):
        
        item = self.tree.currentItem()
        if not item:
            return

        index = self.tree.indexOfTopLevelItem(item)
        
        if index <= 0:  
            return

        self.tree.takeTopLevelItem(index)
        self.tree.insertTopLevelItem(index - 1, item)
        self.tree.setCurrentItem(item)
    
    def move_down(self):
        
        item = self.tree.currentItem()
        if not item:
            return

        index = self.tree.indexOfTopLevelItem(item)
        last_index = self.tree.topLevelItemCount() - 1

        if index < 0 or index >= last_index:  
            return

        self.tree.takeTopLevelItem(index)
        self.tree.insertTopLevelItem(index + 1, item)
        self.tree.setCurrentItem(item)