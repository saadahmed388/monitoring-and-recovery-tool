# ---------------- ui/main_window.py ----------------
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt5.QtGui import QIcon
from config.db_configs import ENVIRONMENTS, DB_CONFIGS
from core.db_config_manager import DBConfigManager
from core.db_client import DBClient
from core.staging import StagingManager
from ui.results_view import ResultsTab
from ui.queries_view import QueriesTab
from ui.pending_view import PendingTab
from ui.connections_view import ConnectionsTab
from ui.sql_sheets_view import SQLSheetsTab
from ui.recovery_templates_view import RecoveryTemplatesTab
from utilities.stylesheets import StylingManager
from core.query_manager import QueryManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Siebel Monitoring & Recovery')
        self.setWindowIcon(QIcon("assets/app_icon.png"))
        self.resize(1400, 800)
           
        self.db_clients = {}
        self.db_config_manager = DBConfigManager()
        self.staging_manager = StagingManager()
        self.query_manager = QueryManager()
        self.styling_manager = StylingManager()
        self.connections_tab = ConnectionsTab(self.db_clients, self.db_config_manager, self.styling_manager)
        self.queries_tab = QueriesTab(self.db_clients, self.staging_manager, self.query_manager, self.styling_manager)

        tabs = QTabWidget()
        tabs.addTab(self.connections_tab, 'Connections')
        tabs.addTab(self.queries_tab, 'Monitoring Queries')
        tabs.addTab(ResultsTab(self.db_clients, self.staging_manager, self.query_manager, self.styling_manager, self.connections_tab, self.queries_tab), 'Results')
        tabs.addTab(PendingTab(self.staging_manager, self.db_clients, self.query_manager, self.styling_manager), 'Pending Changes')
        tabs.addTab(RecoveryTemplatesTab(self.staging_manager,self.query_manager, self.styling_manager), 'Recovery Templates')
        tabs.addTab(SQLSheetsTab(self.db_clients, self.styling_manager), 'SQL Sheet')
        tabs.setStyleSheet(self.styling_manager.tab_style())
        
        self.setCentralWidget(tabs)
