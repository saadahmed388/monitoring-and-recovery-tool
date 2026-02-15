# ================= ui/results_view.py =================
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox
from PyQt5.QtCore import Qt



class ResultsTab(QWidget):
    def __init__(self, db_clients, staging_manager, query_manager):
        
        super().__init__()
        self.db_clients = db_clients
        self.staging_manager = staging_manager
        self.query_manager = query_manager
        layout = QVBoxLayout()
        
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Environment', 'Query Name', 'Row Preview', 'Stage Recovery'])
        self.tree.setColumnWidth(0, 150)
        self.tree.setColumnWidth(1, 200)
        layout.addWidget(self.tree)
        
        self.run_btn = QPushButton('Run All Monitoring Queries')
        self.run_btn.clicked.connect(self.run_all_queries)
        layout.addWidget(self.run_btn)

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

                    for row in results:
                        # Stage result for recovery
                        self.staging_manager.stage_change(
                            env=env,
                            query_name=query_name,
                            row_data=row,
                            sql_template = query_sql   
                        )
                        row_item = QTreeWidgetItem([env, query_name, str(row), 'Stage'])
                        row_item.setFlags(row_item.flags() | Qt.ItemIsUserCheckable)
                        row_item.setCheckState(3, Qt.Checked)
                        self.tree.addTopLevelItem(row_item)
                
                except Exception as e:
                    QMessageBox.warning(
                        self,
                        "Query Execution Failed",
                        f"Error running '{query_name}' on {env}:\n{str(e)}"
                    )
                
        QMessageBox.information(self, 'Run Complete', 'All monitoring queries executed')
        
        
            #for s in self.staging_manager.staged_changes:
            #    if s['env'] != env:
            #       continue
            #    row_item = QTreeWidgetItem([env, s['query_name'], str(s['row_data']), 'Stage'])
            #    row_item.setFlags(row_item.flags() | Qt.ItemIsUserCheckable)
            #    row_item.setCheckState(3, Qt.Checked)
            #    self.tree.addTopLevelItem(row_item)