# ---------------- ui/main_window.py ----------------
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from PyQt5.QtGui import QIcon

from config.db_configs import DB_CONFIGS

from core.managers.connection_manager import ConnectionManager
from core.managers.staging_manager import StagingManager
from core.managers.query_manager import QueryManager
from core.managers.recovery_history_manager import RecoveryHistoryManager
from core.db_client import DBClient

from ui.results_view import ResultsTab
from ui.queries_view import QueriesTab
from ui.staging_view import StagingTab
from ui.connections_view import ConnectionsTab
from ui.sql_sheets_view import SQLSheetsTab
from ui.recovery_history_view import HistoryTab
from ui.recovery_templates_view import RecoveryTemplatesTab

from utilities.stylesheets import StylingManager
from utilities.signal_bus import SignalBus


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Siebel Monitoring & Recovery')
        self.setWindowIcon(QIcon("assets/app_icon.png"))
        self.resize(1400, 800)
        
        self.connection_manager = ConnectionManager()
        self.staging_manager = StagingManager()
        self.query_manager = QueryManager()
        self.styling_manager = StylingManager()
        self.recovery_history_manager = RecoveryHistoryManager()
        self.signal_bus = SignalBus()


        self.db_clients = self.connection_manager.get_all_clients()

        self.connections_tab = ConnectionsTab(self.connection_manager, self.styling_manager)
        self.queries_tab = QueriesTab(self.db_clients, self.staging_manager, self.query_manager, self.styling_manager)
        self.results_tab = ResultsTab(self.staging_manager, self.query_manager, self.connection_manager, self.styling_manager, self.signal_bus)
        self.staging_tab = StagingTab(self.db_clients, self.staging_manager, self.query_manager, self.connection_manager, self.recovery_history_manager, self.styling_manager, self.signal_bus)
        self.history_tab = HistoryTab(self.recovery_history_manager, self.styling_manager)
        self.recovery_templates_tab = RecoveryTemplatesTab(self.staging_manager,self.query_manager, self.styling_manager)
        self.sql_sheets_tab = SQLSheetsTab(self.db_clients, self.styling_manager)

        tabs = QTabWidget()
        tabs.addTab(self.connections_tab, 'Connections')
        tabs.addTab(self.queries_tab, 'Monitoring Queries')
        tabs.addTab(self.results_tab, 'Results')
        tabs.addTab(self.staging_tab, 'Recovery Staging')
        tabs.addTab(self.history_tab, 'Recovery History')
        tabs.addTab(self.recovery_templates_tab, 'Recovery Templates')
        tabs.addTab(self.sql_sheets_tab, 'SQL Sheet')
        tabs.setStyleSheet(self.styling_manager.tab_style())
        
        self.setCentralWidget(tabs)
