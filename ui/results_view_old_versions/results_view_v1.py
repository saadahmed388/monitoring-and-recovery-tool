# ================= ui/results_view.py =================
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem,
    QMessageBox, QTableWidget, QTableWidgetItem, QFrame
)
from PyQt5.QtCore import Qt



class ResultsTab(QWidget):
    def __init__(self, db_clients, staging_manager, query_manager):
        super().__init__()
        self.db_clients = db_clients
        self.staging_manager = staging_manager
        self.query_manager = query_manager
        layout = QVBoxLayout()
        
        
        self.run_btn = QPushButton('Run All Monitoring Queries')
        self.run_btn.clicked.connect(self.run_all_queries)
        layout.addWidget(self.run_btn)


        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Environment', 'Query Name', 'Stage Recovery', 'Row Preview'])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 200)
        self.tree.setColumnWidth(2, 100)
        layout.addWidget(self.tree)
        
        self.setLayout(layout)

    def run_all_queries(self):
        self.tree.clear()
        total_found = 0      
        
        for env, client in self.db_clients.items():
            
            queries = self.query_manager.get_all_queries()
            if not queries:
                QMessageBox.information(self, "No Queries Added", "Please add monitoring queries first.")
                return
                
            for query_def in queries:
                query_name = query_def['name']
                query_sql = query_def['sql']

                try:
                    # ✅ Execute the monitoring SQL
                    results = client.execute_select(query_sql)
                    if not results:
                        continue  # nothing found
                        
                    # parent node for each query result
                    parent_item = QTreeWidgetItem([env, query_name])
                    parent_item.setExpanded(True)
                    self.tree.addTopLevelItem(parent_item)

                    # Build a mini table for each query’s result set
                    table_widget = self._create_table(results)
                    self.tree.setItemWidget(parent_item, 3, table_widget)

                    # Add a staging checkbox for this query
                    parent_item.setFlags(parent_item.flags() | Qt.ItemIsUserCheckable)
                    parent_item.setCheckState(2, Qt.Checked)

                    for row in results:
                        # Stage result for recovery
                        self.staging_manager.stage_change(
                            env=env,
                            query_name=query_name,
                            row_data=row,
                            sql_template = query_sql   
                        )
                        #row_item = QTreeWidgetItem([env, query_name, str(row), 'Stage'])
                        #row_item.setFlags(row_item.flags() | Qt.ItemIsUserCheckable)
                        #row_item.setCheckState(3, Qt.Checked)
                        #self.tree.addTopLevelItem(row_item)
                
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Query Execution Failed",
                        f"Error running '{query_name}' on {env}:\n{str(e)}"
                    )
                
        QMessageBox.information(self, 'Run Complete', 'All monitoring queries executed')
        
        
    def _create_table(self, rows):
        if not rows:
            return None

        cols = list(rows[0].keys())
        table = QTableWidget(len(rows), len(cols))
        table.setHorizontalHeaderLabels(cols)
        table.setAlternatingRowColors(True)
        table.setFrameShape(QFrame.Box)
        table.setStyleSheet("QTableWidget { background-color: #fafafa; }")

        for i, row in enumerate(rows):
            for j, col in enumerate(cols):
                val = str(row[col]) if row[col] is not None else ""
                table.setItem(i, j, QTableWidgetItem(val))

        table.resizeColumnsToContents()
        table.setMinimumHeight(min(300, 30 * (len(rows) + 1)))  # auto-resize height for readability
        return table
