from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout
from PyQt5.QtCore import QObject, Qt, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed
from utilities.stylesheets import StylingManager
from time import time
import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.db_client import DBClient
    from core.managers.staging_manager import StagingManager
    from core.managers.query_manager import QueryManager
    from core.managers.connection_manager import ConnectionManager
    

logger = logging.getLogger(__name__)

class MonitoringWorker(QObject):

    error = pyqtSignal(str) 
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)

    def __init__(self, db_clients, connection_manager: ConnectionManager, query_manager: QueryManager, staging_manager: StagingManager):
        super().__init__()

        self.db_clients = db_clients
        self.query_manager = query_manager
        self.staging_manager = staging_manager
        self.connection_manager = connection_manager
        self.results_map = {}
        self.styling_manager = StylingManager()

    def run(self):
        self.staging_manager.clear_staging_list()
        tasks = []
        connections = self.connection_manager.get_all_connections()
        active_queries = self.query_manager.get_active_queries()
        
        with ThreadPoolExecutor(max_workers=8) as executor:
           
            if not active_queries:
                    self.error.emit('No Active queries')
                    return
                
            for env, client in self.db_clients.items():
                
                for query in active_queries:

                    query_name = query['name']
                    query_sql = query['sql']
                    auto_recovery = query['auto_recovery']

                    futures = executor.submit(
                        self.run_query, 
                        client, 
                        query_sql, 
                        env, 
                        query_name,
                        auto_recovery,
                        time(),
                        self.staging_manager
                    )
                    tasks.append(futures)
                
            for future in as_completed(tasks):
                try:
                    future.result()
                except Exception as e:
                    logger.exception(str(e))
                else:
                    pass

        self.finished.emit(self.results_map)
        
    def run_query(self, client: DBClient, query_sql, env, query_name, auto_recovery, start_time, staging_manager: StagingManager):
        try:
            results = client.execute_select(query_sql)
            if not results:
                logger.info(f'[{env}] {query_name} | Duration: {time() - start_time} | NA')
            else:
                self.results_map[env, query_name] = results
                if auto_recovery == "Y":
                    self.staging_manager.stage_change(env, query_name, results)
                logger.info(f'[{env}] {query_name} | Duration: {time() - start_time}  | Rows: {len(results)} | Row IDs: {self.get_row_ids(results)}')
        except Exception as e:
            logger.exception(f'Error running \'{query_name}\' on {env}:\n{str(e)}')
            self.error.emit(f'Error running \'{query_name}\' on {env}:\n{str(e)}')
    
    def get_row_ids(self, result: list[dict]):
        row_ids = []
        if 'ROW_ID' in result[0].keys():
            for row in result:
                row_ids.append(row['ROW_ID'])
        return row_ids
