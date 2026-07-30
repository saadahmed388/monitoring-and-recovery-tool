from __future__ import annotations
import traceback

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QTreeWidget, 
                             QTreeWidgetItem, QInputDialog, QMessageBox, QHBoxLayout, QStyle)
from utilities.sql_formatting import SqlPreviewV2
from utilities.custom_widgets import StyledInputDialog

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.managers.query_manager import QueryManager
    from core.managers.staging_manager import StagingManager

class RecoveryTemplatesTab(QWidget):
    def __init__(self, staging_manager: StagingManager, query_manager: QueryManager, styling_manager):
        super().__init__()
        self.staging_manager = staging_manager
        self.styling_manager = styling_manager
        self.query_manager = query_manager
        self.queries = self.query_manager.get_all_queries()

        layout = QVBoxLayout()
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Query Name', 'Recovery Scheme', 'Auto Recovery Template', 'Verification Template', 'Binder Column'])
        self.tree.setColumnWidth(0, 500)
        self.tree.setColumnWidth(1, 200)
        self.tree.setColumnWidth(2, 250)
        self.tree.setColumnWidth(3, 250)
        self.tree.setIndentation(0)
        self.tree.setStyleSheet(self.styling_manager.header_style())
        layout.addWidget(self.tree)
        
        # Create a horizontal bar for buttons
        button_bar = QHBoxLayout()

        self.edit_binder_btn = QPushButton('Edit Binder')
        self.edit_binder_btn.setStyleSheet(self.styling_manager.button_style())
        button_bar.addWidget(self.edit_binder_btn)
        layout.addLayout(button_bar)

        self.setLayout(layout)
        
        self.query_manager.queries_updated.connect(self.load_templates)
        self.sql_preview = None
        self.edit_binder_btn.clicked.connect(self.change_binder_col) 

        self.load_templates()
           
    def load_templates(self):
        self.tree.clear()
        if self.queries:
            for q in self.queries:
                name = q.get("name", "")
                binder_col = q.get("binder_col", "")
                auto_recovery_enabled = q.get("auto_recovery", "")
                recovery_template = q.get("recovery_template", "")
                verification_template = q.get("verification_template", "")

                recovery_template_status = 1 if not recovery_template else 0
                auto_recovery_template_status = 1 if auto_recovery_enabled == "N" else 0
                verification_template_status = 1 if not verification_template else 0

                item = QTreeWidgetItem([name, '', '', '', binder_col])
                self.tree.addTopLevelItem(item)

                if recovery_template_status:
                    template_preview_btn = QPushButton("No Template")
                else:
                    template_preview_btn = QPushButton()
                    template_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                template_preview_btn.setFlat(True)
                template_preview_btn.clicked.connect(lambda _ : self.show_template(mode = "manual"))
                self.verification_preview_btn_cv = template_preview_btn

                if auto_recovery_template_status:
                    auto_template_preview_btn = QPushButton("No Template")
                else:
                    auto_template_preview_btn = QPushButton()
                    auto_template_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                auto_template_preview_btn.setFlat(True)
                auto_template_preview_btn.clicked.connect(lambda  _ : self.show_template(mode = "auto"))
                self.auto_template_preview_btn_cv = auto_template_preview_btn

                if verification_template_status:
                    verification_preview_btn = QPushButton("No Template")
                else:
                    verification_preview_btn = QPushButton()
                    verification_preview_btn.setIcon(self.style().standardIcon(QStyle.SP_FileDialogDetailedView))
                verification_preview_btn.setFlat(True)
                verification_preview_btn.clicked.connect(lambda  _ : self.show_template(mode = "verify"))
                self.verification_preview_btn_cv = verification_preview_btn

                self.tree.setItemWidget(item, 1, template_preview_btn)
                self.tree.setItemWidget(item, 2, auto_template_preview_btn)
                self.tree.setItemWidget(item, 3, verification_preview_btn)

    
    def show_template(self, mode, template = None, rownum = None):
        try:
            if self.sql_preview is not None:
                self.sql_preview.close()
                self.sql_preview.deleteLater()
                self.sql_preview = None
            
            match mode:
                case "auto" | "verify":
                    if rownum is not None:
                        item = self.tree.topLevelItem(rownum)
                        curr_item = item
                    else:    
                        curr_item = self.tree.currentItem()
                    q_name = curr_item.text(0)
                    auto_enabled = [1 for q in self.queries if q['name'] == q_name and q['auto_recovery'] == 'Y']
                    if not auto_enabled:
                        QMessageBox.information(self, 'Recovery Template Update', f'This query is not configured for auto-recovery')
                        return

            if not template:
                template = self.get_template(mode)
            self.sql_preview = SqlPreviewV2(template, mode, edit_func=self.edit_template, save_func=self.save_template)
            self.sql_preview.preview_mode()
        
        except Exception:
            traceback.print_exc()
    
    def edit_template(self, template, mode):
        try:
            if self.sql_preview is not None:
                self.sql_preview.close()
                self.sql_preview.deleteLater()
                self.sql_preview = None
            self.sql_preview = SqlPreviewV2(template, mode, edit_func=self.edit_template, save_func=self.save_template)
            self.sql_preview.edit_mode()
        
        except:
            traceback.print_exc()
        
    def template_name(self, temp):
        t_n = {
            "recovery_template": "Recovery Scheme",
            "auto_recovery_template": " Auto recovery SQL",
            "verification_template": "Verification SQL"
        }

        return t_n[temp]

    def save_template(self, template, mode):
        curr_item = self.tree.currentItem()
        row_num = self.tree.indexOfTopLevelItem(curr_item)
        name = curr_item.text(0)

        match mode:
            case "manual":
                temp_col = "recovery_template"
            case "auto":
                temp_col = "auto_recovery_template"
            case "verify":
                temp_col = "verification_template"
        
        for q in self.queries:
            if (q["name"] == name):
                if not template:
                    q[temp_col] = ""
                else:
                    q[temp_col] = template
                self.query_manager.save_queries()
                QMessageBox.information(self, 'Updated', f'{self.template_name(temp_col)} for {name} updated')
                break

        #self.show_template(mode, template, row_num)

    def get_template(self, mode):
        queries = self.query_manager.get_all_queries()
        curr_item = self.tree.currentItem()
        q_name = curr_item.text(0)
        match mode:
            case "manual":
                template = [q['recovery_template'] for q in queries if q['name'] == q_name]
            case "auto":
                template = [q['auto_recovery_template'] for q in queries if q['name'] == q_name]
            case "verify":
                template = [q['verification_template'] for q in queries if q['name'] == q_name]
        
        return template[0]

    def change_binder_col(self):
        queries = self.query_manager.get_all_queries()
        curr_item = self.tree.currentItem()
        curr_binder_col = curr_item.text(3)
        q_name = curr_item.text(0)
        
        binder_col = [q['binder_col'] for q in queries if q['name'] == q_name and q['auto_recovery'] == 'Y']
        if not binder_col:
            QMessageBox.information(self, 'Binder Column Update', f'This query is not configured for auto-recovery')
            return
        
        new_col, ok1 = StyledInputDialog("Binder Column Update", "Enter column name:", "N", curr_binder_col).get_text()
        if not ok1 or not new_col:
            return
        
        for q in queries:
            if q['name'] == q_name and q['auto_recovery'] == 'Y':
                q['binder_col'] = new_col
                self.query_manager.save_queries()
                break





