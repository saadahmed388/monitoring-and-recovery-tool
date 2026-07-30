from __future__ import annotations

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QTreeWidget, QTreeWidgetItem, QApplication, QShortcut, QMessageBox, QTableWidget, QTableWidgetItem, QFrame, QDialog, QStyle, QHeaderView, QHBoxLayout
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtGui import QKeySequence
from workers.monitoring_worker import MonitoringWorker

import logging

from typing import TYPE_CHECKING

if TYPE_CHECKING:
  from core.managers.staging_manager import StagingManager
  from core.managers.query_manager import QueryManager
  from core.managers.connection_manager import ConnectionManager

logger = logging.getLogger(__name__)
class ResultsTab(QWidget):
  def __init__(self, staging_manager: StagingManager, query_manager: QueryManager, connection_manager: ConnectionManager, styling_manager, signal_bus):
    super().__init__()

    self.signal_bus = signal_bus
    self.staging_manager = staging_manager
    self.query_manager = query_manager
    self.styling_manager = styling_manager
    self.connection_manager = connection_manager
    
    layout = QVBoxLayout()
    self.tree = QTreeWidget()
    self.tree.setHeaderLabels(['Environment','Query Name','Row Preview','Stage Recovery'])
    self.tree.setIndentation(0)
    self.tree.setColumnWidth(0,200)
    self.tree.setColumnWidth(1,600)
    self.tree.setColumnWidth(2,250)
    self.tree.setColumnWidth(3,250)
    self.tree.setStyleSheet(self.styling_manager.header_style())
    layout.addWidget(self.tree)
    
    button_bar = QHBoxLayout()
    
    self.run_btn = QPushButton('Run All Monitoring Queries')
    self.run_btn.setStyleSheet(self.styling_manager.button_style())
    button_bar.addWidget(self.run_btn)
    
    layout.addLayout(button_bar)
    self.setLayout(layout)
    
    self.run_btn.clicked.connect(self.run_all_queries)

  def run_all_queries(self):
    self.tree.clear()
    self.db_clients = self.connection_manager.get_all_clients()
    self.monitoring_worker = MonitoringWorker(self.db_clients, self.connection_manager, self.query_manager, self.staging_manager)
    self.monitoring_worker_thread = QThread()
    self.monitoring_worker.moveToThread(self.monitoring_worker_thread)
    self.monitoring_worker_thread.started.connect(self.monitoring_worker.run)
    self.monitoring_worker_thread.finished.connect(self.monitoring_worker_thread.deleteLater)
    self.monitoring_worker.finished.connect(self.on_worker_completion)
    self.monitoring_worker.finished.connect(self.monitoring_worker_thread.quit)
    self.monitoring_worker.finished.connect(self.monitoring_worker.deleteLater)
    self.monitoring_worker.error.connect(lambda msg: self.on_error(msg))
    self.monitoring_worker_thread.start()
    logger.info('Thread Started')

  def on_worker_completion(self,results_map):
    self.add_to_tree(results_map)
    self.signal_bus.global_signal.emit()
    logger.info('All monitoring queries executed')
    QMessageBox.information(self,'Run Complete','All monitoring queries executed')

  def on_error(self,message):
    logger.error(message)
    QMessageBox.warning(self,'Error',message)

  def add_to_tree(self,results_map):
    self.tree.clear()
    for k,v in results_map.items():
      env = k[0]
      query_name = k[1]
      item = QTreeWidgetItem([env,query_name,'',''])
      self.tree.addTopLevelItem(item)
      preview_btn = QPushButton()
      preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
      preview_btn.setFlat(True)
      preview_btn.clicked.connect(lambda _,e=env,q=query_name,r=results_map: self.show_table(e,q,r))
      self.tree.setItemWidget(item,2,preview_btn)
      item.setFlags(item.flags()|Qt.ItemIsUserCheckable)
      item.setCheckState(3,Qt.Checked)

  def show_table(self, env, query_name, results_map):

    rows = results_map.get((env, query_name), [])
    
    if not rows:
        QMessageBox.information(self, "No Data", "No rows available for this query.")
        return

    dialog = QDialog(self)
    dialog.setWindowTitle(f"{env} - {query_name}")
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