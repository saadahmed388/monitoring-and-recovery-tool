from __future__ import annotations
import traceback

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTreeWidget, 
                            QTreeWidgetItem, QMessageBox, QHBoxLayout, QTableWidget, QTableWidgetItem,
                            QDialog, QStyle, QLineEdit, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from utilities.sql_formatting import SqlPreview
from utilities.custom_widgets import StyledInputDialog

from typing import TYPE_CHECKING
from core.db_client_isl import DBClientISL
from config.db_configs import ENVIRONMENTS_DSN

import logging
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from core.managers.connection_manager import ConnectionManager
    from core.managers.query_manager import QueryManager
    from core.managers.staging_manager import StagingManager
    from core.managers.recovery_history_manager import RecoveryHistoryManager

class StagingTab(QWidget):
    
    staging_updated = pyqtSignal()
    
    def __init__(self, read_db_clients, staging_manager: StagingManager, query_manager: QueryManager, connection_manager: ConnectionManager, recovery_history_manager: RecoveryHistoryManager, styling_manager, signal_bus):
        super().__init__()
        self.staging_manager = staging_manager
        self.styling_manager = styling_manager
        self.query_manager = query_manager
        self.read_db_clients = read_db_clients
        self.signal_bus = signal_bus
        self.recovery_history_manager = recovery_history_manager
        
        self.db_clients_isl = {}
        self.pool_conns = {}

        layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Include', 'Env', 'Query', 'Record Data (Intial)', 'Status', 'Record Data (Current)',  'RT', 'ART', 'VT', 'Connection'])
        self.tree.setColumnWidth(0, 90)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(3, 200)
        self.tree.setColumnWidth(4, 100)
        self.tree.setColumnWidth(5, 200)
        self.tree.setColumnWidth(6, 50)
        self.tree.setColumnWidth(7, 50)
        self.tree.setColumnWidth(8, 50)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)

        
        # Create a horizontal bar for buttons
        button_bar = QHBoxLayout()     

        self.select_all_btn = QPushButton('Select All')
        self.deselect_all_btn = QPushButton('Deselect All')
        self.recover_all_btn = QPushButton('Recover All')
        self.commit_all_btn = QPushButton('Commit All')
        self.rollback_all_btn = QPushButton('Rollback All')
        self.recover_selected_btn = QPushButton('Recover')
        self.commit_selected_btn = QPushButton('Commit')
        self.rollback_selected_btn = QPushButton('Rollback')


        self.select_all_btn.setStyleSheet(self.styling_manager.button_style())
        self.deselect_all_btn.setStyleSheet(self.styling_manager.button_style())        
        self.recover_all_btn.setStyleSheet(self.styling_manager.button_style())
        self.commit_all_btn.setStyleSheet(self.styling_manager.button_style())
        self.rollback_all_btn.setStyleSheet(self.styling_manager.button_style())
        self.recover_selected_btn.setStyleSheet(self.styling_manager.button_style())
        self.commit_selected_btn.setStyleSheet(self.styling_manager.button_style())
        self.rollback_selected_btn.setStyleSheet(self.styling_manager.button_style())

        button_bar.addWidget(self.recover_all_btn)
        button_bar.addWidget(self.commit_all_btn)
        button_bar.addWidget(self.rollback_all_btn)
        button_bar.addWidget(self.recover_selected_btn)
        button_bar.addWidget(self.commit_selected_btn)
        button_bar.addWidget(self.rollback_selected_btn)

        layout.addLayout(button_bar)
        self.setLayout(layout)

        self.recover_selected_btn.clicked.connect(self.recover_selected)
        self.commit_selected_btn.clicked.connect(self.commit_selected)
        self.rollback_selected_btn.clicked.connect(self.rollback_selected)
        self.recover_all_btn.clicked.connect(self.recover_all)
        self.commit_all_btn.clicked.connect(self.commit_all)
        self.rollback_all_btn.clicked.connect(self.revert_all)
        self.signal_bus.global_signal.connect(self.refresh_tree)
        self.staging_updated.connect(self.refresh_tree)

        app = QApplication.instance()
        if app:
            app.aboutToQuit.connect(self.close_conns)

    def close_conns(self):
        print("Closing connections")
        for conn in self.pool_conns.values():
            try:
                conn.rollback()
                conn.close()
            except Exception:
                logger.exception("Error closing connection")
        self.pool_conns.clear()

    def refresh_tree(self):
        self.tree.clear()
        if self.pool_conns:
            self.close_conns()
        
        for s in self.staging_manager.staged_changes:
            item = QTreeWidgetItem(['', s['env'], s['query_name'], '', 'Pending', '', '', '', '', 'No Connection'])
            
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(0, Qt.Checked if s['include'] else Qt.Unchecked)
            self.tree.addTopLevelItem(item)

            preview_btn = QPushButton()
            preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            preview_btn.setFlat(True)
            preview_btn.clicked.connect(lambda _, e=s['env'], q=s['query_name'], d=s['row_data'] : self.show_table(e,q,d))
            self.tree.setItemWidget(item,3, preview_btn)

            rt_preview_btn = QPushButton()
            rt_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            rt_preview_btn.setFlat(True)
            rt_preview_btn.clicked.connect(lambda _, t = 'rt': self.show_template(type = t))
            self.tree.setItemWidget(item, 6, rt_preview_btn)

            art_preview_btn = QPushButton()
            art_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            art_preview_btn.setFlat(True)
            art_preview_btn.clicked.connect(lambda _, t = 'art': self.show_template(type =t))
            self.tree.setItemWidget(item, 7, art_preview_btn)

            vt_preview_btn = QPushButton()
            vt_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            vt_preview_btn.setFlat(True)
            vt_preview_btn.clicked.connect(lambda _, t = 'vt': self.show_template(type = t))
            self.tree.setItemWidget(item, 8, vt_preview_btn)

            recovery_preview_btn = QPushButton()
            recovery_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
            recovery_preview_btn.setFlat(True)
            recovery_preview_btn.clicked.connect(self.check_post_rec)
            self.tree.setItemWidget(item, 5, recovery_preview_btn)


    def show_table(self, env, query_name, data):
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle(f"{env} - {query_name}")
            dialog.resize(800, 400)

            layout = QVBoxLayout(dialog)

            table = QTableWidget(len(data),len(data[0].keys()))
            table.setHorizontalHeaderLabels(list(data[0].keys()))

            if not data:
                QMessageBox(self, "Info", "No data to show")
                return

            for row_idx, row in enumerate(data):
                for col_idx, col in enumerate(row.keys()):
                    table.setItem(row_idx, col_idx, QTableWidgetItem(str(row.get(col, ""))))

            table.resizeColumnsToContents()
            layout.addWidget(table)
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            close_btn.setStyleSheet(self.styling_manager.button_style())
            layout.addWidget(close_btn)

            dialog.exec_()
        
        except Exception:
            logger.exception("Unhandled Exception")
    
    def get_template(self, type = None):
        try:
            curr_item = self.tree.currentItem()
            q_name = curr_item.text(2) 
            queries = self.query_manager.get_all_queries()
            if type == 'rt':
                template = [t['recovery_template'] for t in queries if t['name'] == q_name]
            elif type == 'art':
                template = [t['auto_recovery_template'] for t in queries if t['name'] == q_name]
            elif type == 'vt':
                template = [t['verification_template'] for t in queries if t['name'] == q_name]                        
            template = template[0]
            return template
        except Exception:
            logger.exception("Unhandled Exception")
    
    def show_template(self, template = None, type = None):
        try:
            if not template:
                template = self.get_template(type)
            self.sql_preview = SqlPreview(template)
            self.sql_preview.show()
        except Exception:
            traceback.print_exc()

    def commit_all(self):
        self.staging_manager.commit_all(self.db_clients)
        self.refresh_tree()
        QMessageBox.information(self, 'Commit', 'Committed all included staged changes')

    def revert_all(self):
        self.staging_manager.revert_all(self.db_clients)
        self.refresh_tree()
        QMessageBox.information(self, 'Revert', 'Reverted committed changes')

    def get_verification_data(self, query_name):
        
        try:
            queries = self.query_manager.get_all_queries()    
            for q in queries:
                if q['name'] == query_name:
                    verification_template = q['verification_template']
        except Exception:
            logger.exception("Unhandled Exception")

    def get_recovery_data(self, query_name):
        try:
            queries = self.query_manager.get_all_queries()
            for q in queries:
                if q['name'] == query_name and q['auto_recovery'] == 'Y':
                    return q['auto_recovery_template'], q['verification_template'], q['binder_col']
        except:
            logger.exception("Unhandled Exception")


    def get_bind_data(self, row_data, bind_col):
        try:
            if not row_data:
                QMessageBox.warning(self, "Binder Data", "Row set empty. No binder column found!")
                return
                #raise ValueError("Row set empty. Now binder column found!")
            
            first_row = row_data[0][0]
            key_lowercase = {str(key).lower(): key for key in first_row}
            
            if str(bind_col).lower() not in key_lowercase:
                QMessageBox.warning(self, "Binder Data", f"Column {bind_col} not found in row set data\n Enter correct binder column to proceed.")
                return
            
            bind_vars_list = []
            for d in row_data[0]:
                bind_col = key_lowercase.get(str(bind_col).lower(), "")
                bind_var = d.get(bind_col, "")
                bind_vars_list.append(bind_var)
            
            bind_vars = "', '".join(bind_vars_list)
            return f"('{bind_vars}')"
        
        except:
            logger.exception("Unhandled Exception")

    def get_db_pools(self, username, password):
        try:
            db_pools = {}
            failed_connections = {}
            
            for env, dsn in ENVIRONMENTS_DSN.items():
                try:
                    db_pools[env] = DBClientISL(username, password, dsn)
                except Exception as e:
                    failed_connections[env] = str(e)
            
            if failed_connections:
                error_details = "\n".join(
                        f"{envi}: {error}" for envi, error in failed_connections.items()
                    ) 
                raise Exception(f"Failed to connect to the following environments:\n{error_details}")
            
            return db_pools
        except:
            logger.exception("Unhandled Exception")

    
    def recover_selected(self):
        try:
            curr_item = self.tree.currentItem() 
            
            if not curr_item:
                QMessageBox.warning(self, "No Selection", "Please select an entity to perform recovery.")
                return  
            
            env_name = curr_item.text(1)
            query_name = curr_item.text(2)
            status = curr_item.text(4)
            
            if status == 'Staged':
                QMessageBox.warning(self, "Recovery", "Records already staged\nEither Commit or Rollback Changes")
                return

            if status == 'Committed':
                QMessageBox.warning(self, "Recovery", "Records already commitedt\nStep not required")
                return
           
            for k, v in self.db_clients_isl.items():
                print(k, v.connected)
            print(self.pool_conns)

            if env_name not in self.db_clients_isl.keys():
                if not self.perform_isl_connection(env_name):
                    return
            else:
                if not self.db_clients_isl[env_name].connected:
                    if not self.perform_isl_connection(env_name):
                        return        

            if (env_name, query_name) not in self.pool_conns.keys(): 
                connection = self.get_connection(env_name)                
                self.pool_conns[(env_name, query_name)] = connection
                curr_item.setText(9, f"{connection.username}@{connection.dsn}")

            row_data = [
                s['row_data']
                for s in self.staging_manager.staged_changes
                if s['env'] == env_name
                and s['query_name'] == query_name
            ]
        
            art, vt, bind_col = self.get_recovery_data(query_name)
            bind_vars = self.get_bind_data(row_data, bind_col)
            art = art.replace(":bind", bind_vars) 
        
            db_client_conn = self.pool_conns[(env_name, query_name)]
            count = self.db_clients_isl[env_name].execute_conn_dml(db_client_conn, art)

            curr_item.setText(4, "Staged")
            QMessageBox.information(self, "DML", 
                                    f"Updates Staged for commit for Query: {query_name} in  Env: {env_name}\
                                        \nCount of records: {count}")
    
        except:
            logger.exception("Unhandled Exception")

    def recover_all(self):
        pass

    def commit_selected(self):
        try:
            curr_item = self.tree.currentItem() 
            env_name = curr_item.text(1)
            query_name = curr_item.text(2)

            db_client_conn = self.pool_conns[(env_name, query_name)]
            self.db_clients_isl[env_name].commit_conn(db_client_conn)         
            curr_item.setText(4, "Committed")

            for s in self.staging_manager.staged_changes:
                if s['env'] == env_name and s['query_name'] == query_name:
                    
                    row_data = [s.get('row_data',[])]

                    art, vt, bind_col = self.get_recovery_data(query_name)
                    bind_vars = self.get_bind_data(row_data, bind_col)
                    vt = vt.replace(":bind", bind_vars)
                    
                    db_client_conn = self.pool_conns[(env_name, query_name)]
                    result = self.db_clients_isl[env_name].execute_conn_select(db_client_conn, vt)
                    
                    s['restored_data'] = result

                    self.recovery_history_manager.add_history(query_name, env_name, s["row_data"], s["restored_data"])
                    self.recovery_history_manager.save_history()
            
            QMessageBox.information(self, "Commit Changes", f"Changes Committed for Query: {query_name} in  Env: {env_name}")

        except Exception:
            logger.exception("Unhandled Exception")

    def commit_all(self):
        pass

    def rollback_selected(self):
        try:
            curr_item = self.tree.currentItem() 
            env_name = curr_item.text(1)
            query_name = curr_item.text(2)

            db_client_conn = self.pool_conns[(env_name, query_name)]
            self.db_clients_isl[env_name].rollback_conn(db_client_conn)         
            curr_item.setText(4, "Pending")

            QMessageBox.information(self, "Rollback Changes", f"Changes Rolled back for Query: {query_name} in  Env: {env_name}")

        except Exception:
            logger.exception("Unhandled Exception")
                    

    def rollback_all(self):
        pass

    
    def check_post_rec(self):
        try:
            curr_item = self.tree.currentItem() 
            env_name = curr_item.text(1)
            query_name = curr_item.text(2)

            if env_name not in self.db_clients_isl.keys():
                if not self.perform_isl_connection(env_name):
                    return
            else:
                if not self.db_clients_isl[env_name].connected:
                    if not self.perform_isl_connection(env_name):
                        return        

            if (env_name, query_name) not in self.pool_conns.keys():   
                connection = self.get_connection(env_name)                
                self.pool_conns[(env_name, query_name)] = connection
                print(connection.autocommit)
                curr_item.setText(9, f"{connection.username}@{connection.dsn}")
            
            row_data = [
                s['row_data']
                for s in self.staging_manager.staged_changes
                if s['env'] == env_name
                and s['query_name'] == query_name
            ]
        
            art, vt, bind_col = self.get_recovery_data(query_name)
            bind_vars = self.get_bind_data(row_data, bind_col)
            vt = vt.replace(":bind", bind_vars)
        
            db_client_conn = self.pool_conns[(env_name, query_name)]
            result = self.db_clients_isl[env_name].execute_conn_select(db_client_conn, vt)

            self.show_table(env_name, query_name, result)

        except:
            logger.exception("Unhandled Exception")

    def perform_isl_connection(self, env):
        try:
            username, ok2 = StyledInputDialog(f"Username", "Enter Update Priviledged Username:").get_text()
            if not ok2 or not username:
                return  False
            password, ok3 = StyledInputDialog(f"Password", "Enter Update Priviledged Password:").get_text()
            if not ok3 or not password:
                return  False
                
            self.db_clients_isl[env] = DBClientISL(ENVIRONMENTS_DSN[env])
            self.db_clients_isl[env].create_pool(username, password)
            return True
        
        except Exception as e: 
            logger.exception("Unhandled Exception")
            QMessageBox.critical(self, "Login Denied", f'{env} - {str(e)}')
            return False

    def get_connection(self, env):
        return self.db_clients_isl[env].get_conn()

    def update_connection_metadata(self, env_name, query_name, connection):
        for s in self.staging_manager.staged_changes:
            if s['env'] == env_name and s['query_name'] == query_name:
                s['db_connection'] = f"{connection.username}@{connection.dsn}"
                self.staging_updated.emit()
                break
                
    
        
        
        
